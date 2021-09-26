from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from orders.models import Account, Wallet, Order
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
    get_object_or_404,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    AccountDisplaySerializer, AccountUpdateSerializer,
    RegistrationSerializer,
    WalletAddSerializer, WalletDisplaySerializer,
    WalletUpdateSerializer, WalletCreateSerializer,
    OrderSerializer
)
from .permissions import (
    IsSameAsAuthorOrReadonly, IsSameUserAccountOrReadonly,
)
from django.contrib.auth import get_user_model, logout
from rest_framework.decorators import (
    api_view, permission_classes, authentication_classes
)
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.pagination import PageNumberPagination
from proj_helpers.transaction import Transaction, TransactionError
from proj_helpers.order_perms import get_permissions_for_order


# ----------------ACCOUNT VIEWS------------------------
class AccountListAPIView(ListAPIView):
    queryset = get_user_model().objects.all().order_by('username')
    serializer_class = AccountDisplaySerializer
    pagination_class = None


class DisplayUpdateDeleteAccountAPIView(APIView):
    permission_classes = [IsSameUserAccountOrReadonly, ]
    authentication_classes = [TokenAuthentication, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Account.objects.all()

    def get(self, request, *args, **kwargs):
        username = kwargs.pop('username')
        account = get_object_or_404(self.queryset, username=username)
        serializer = AccountDisplaySerializer(
            account, context={"request": request})
        return Response(serializer.data)

    def put(self, request, username):
        account = get_object_or_404(self.queryset, username=username)
        self.check_object_permissions(request, account)
        serializer = AccountUpdateSerializer(account, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': f'Изменена информация об аккаунте {username}'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username):
        account = get_object_or_404(self.queryset, username=username)
        self.check_object_permissions(request, account)
        # remove user's wallet from currently executing
        # order, if he has one
        if hasattr(account, 'current_order'):
            if hasattr(account.current_order, 'executor_wallet'):
                account.current_order.executor_wallet = None
                account.current_order.save()

        logout(request)
        account.delete()
        return Response({'success': f'Аккаунт {username} успешно удалён.'}, status=status.HTTP_204_NO_CONTENT)


class RegisterAPIView(CreateAPIView):
    serializer_class = RegistrationSerializer
    parser_classes = [MultiPartParser, FormParser, ]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        account = get_user_model().objects.get(
            username=response.data['username'])
        data = {}
        data['token'] = Token.objects.get(user=account).key
        return Response(data)


@api_view(['GET', ])
@authentication_classes([TokenAuthentication, ])
@permission_classes([IsAuthenticated, ])
def get_current_account_detail(request):
    serializer = AccountDisplaySerializer(
        request.user, context={'request': request})
    return Response(serializer.data)


# ----------------ADMIN WALLET VIEWS-------------------
class AdminListDisplayWalletAPIView(ListAPIView):
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]
    serializer_class = WalletDisplaySerializer
    queryset = Wallet.objects.all().order_by('-money')


class AdminCreateWalletAPIView(CreateAPIView):
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]
    serializer_class = WalletCreateSerializer


class AdminUpdateDeleteWalletAPIView(APIView):
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request, walletname):
        wallet = get_object_or_404(Wallet, name=walletname)
        serializer = WalletDisplaySerializer(wallet)
        return Response(serializer.data)

    def patch(self, request, walletname):
        wallet = get_object_or_404(Wallet, name=walletname)
        serializer = WalletUpdateSerializer(
            wallet, data=request.data, partial=True)
        if serializer.is_valid():
            d1 = wallet.__dict__.copy()
            d2 = serializer.save().__dict__
            if d1 == d2:
                return Response(
                    {'success': f'Информация о кошельке {walletname} осталась неизменённой.'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'success': f'Изменена информация о кошельке {walletname}'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, walletname):
        wallet = get_object_or_404(Wallet, name=walletname)
        wallet.delete()
        return Response({'success': f'Кошелёк {walletname} успешно удалён.'}, status=status.HTTP_204_NO_CONTENT)


# ----------------REGULAR WALLET VIEWS-----------------
class ListDisplayWalletAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]
    serializer_class = WalletDisplaySerializer
    pagination_class = None

    def get_queryset(self):
        return Wallet.objects.filter(accounts=self.request.user).order_by('-money')


@api_view(['POST', ])
@authentication_classes([TokenAuthentication, ])
@permission_classes([IsAuthenticated, ])
def add_wallet(request):
    serializer = WalletAddSerializer(data=request.data)
    wallet = serializer.get_wallet()
    if wallet is None:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    request.user.wallets.add(wallet)
    return Response({'success': f'Кошелёк {wallet.name} успешно добавлен к доступным.'}, status=status.HTTP_200_OK)


@api_view(['DELETE', ])
@authentication_classes([TokenAuthentication, ])
@permission_classes([IsAuthenticated, ])
def remove_wallet(request, walletname):
    wallet = get_object_or_404(Wallet, name=walletname)
    if not request.user.wallets.filter(name=walletname).exists():
        return Response({'detail': f'У вас нет кошелька {wallet.name}.'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.wallets.remove(wallet)

    # if we remove wallet from account, it should be also removed
    # from all the orders, which have this wallet attached to them
    # either as orderer_wallet or executor_wallet
    if hasattr(request.user, 'current_order'):
        if hasattr(request.user.current_order, 'executor_wallet'):
            request.user.current_order.executor_wallet = None
            request.user.current_order.save()

    orders_with_this_author_wallet = Order.objects\
        .filter(orderer_wallet__name=walletname)\
        .filter(author__username=request.user.username)

    for order in orders_with_this_author_wallet:
        order.orderer_wallet = None
        order.save()

    return Response({'success': f'Кошелёк {wallet.name} успешно убран из доступных.'}, status=status.HTTP_204_NO_CONTENT)


# ----------------ORDER VIEWS--------------------------
class ListCreateOrderAPIView(ListCreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by('-date_posted')
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code == 200:
            # messages and stuff
            pass
        else:
            # error messages
            pass
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            # messages and stuff
            pass
        else:
            # error messages
            pass
        return response


class DisplayUpdateDeleteOrderAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsSameAsAuthorOrReadonly, ]
    authentication_classes = [TokenAuthentication, ]
    queryset = Order.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            # messages and stuff
            pass
        else:
            # error messages
            pass
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            # messages and stuff
            pass
        else:
            # error messages
            pass
        return response


@api_view(['PATCH', ])
@authentication_classes([TokenAuthentication, ])
@permission_classes([IsAuthenticated, ])
def make_order_action(request, id):
    """
    Использование:
    {"accept_order": true},
    {"reject_order": true},
    {"pick_ord_wallet": "wallet_name"},
    {"pick_exec_wallet": "wallet_name"},
    {"pay_and_delete": true}.\n
    Все остальные запросы будут расценены как ошибочные.
    """
    order = get_object_or_404(Order, id=id)
    perms = get_permissions_for_order(order, request)
    print(perms)

    print(request.data)

    accept_order = request.data.get('accept_order', '')
    reject_order = request.data.get('reject_order', '')
    pick_ord_wallet = request.data.get('pick_ord_wallet', '')
    pick_exec_wallet = request.data.get('pick_exec_wallet', '')
    pay_and_delete = request.data.get('pay_and_delete', '')

    print(accept_order, reject_order, pick_ord_wallet,
          pick_exec_wallet, pay_and_delete)

    if accept_order is True and perms['can_accept']:
        order.executor = request.user
        order.save()
        return Response(
            {'success': f'Пользователь {request.user.username} принял заказ {order}.'}
        )

    elif reject_order is True and perms['can_reject']:
        order.executor = None
        order.executor_wallet = None
        order.save()
        return Response(
            {'success': f'Пользователь {request.user.username} отказался от заказа {order}.'}
        )

    elif isinstance(pick_ord_wallet, str) and pick_ord_wallet.strip() != '' and perms['can_pick_ord_wallet']:
        if pick_ord_wallet.strip() == 'null':
            order.orderer_wallet = None
            order.save()
            return Response(
                {'success': f'Автор {request.user.username} убрал кошелёк для оплаты по заказу \'{order}\'.'}
            )
        wallet = get_object_or_404(
            request.user.wallets, name=pick_ord_wallet.strip())
        if (hasattr(order, 'executor_wallet') and
                order.executor_wallet is not None and
                wallet.name == order.executor_wallet.name
                ):
            return Response(
                {'detail': f'Нельзя выставить тот же кошелёк, что и исполнитель.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.orderer_wallet = wallet
        order.save()
        return Response(
            {'success': f'Автор {request.user.username} выставил кошелёк {wallet} для оплаты по заказу \'{order}\'.'}
        )

    elif isinstance(pick_exec_wallet, str) and pick_exec_wallet.strip() != '' and perms['can_pick_exec_wallet']:
        if pick_exec_wallet.strip() == 'null':
            order.executor_wallet = None
            order.save()
            return Response(
                {'success': f'Исполнитель {request.user.username} убрал кошелёк для начисления средств по заказу \'{order}\'.'}
            )
        wallet = get_object_or_404(
            request.user.wallets, name=pick_exec_wallet.strip())
        if (hasattr(order, 'orderer_wallet') and
                order.orderer_wallet is not None and
                wallet.name == order.orderer_wallet.name
                ):
            return Response(
                {'detail': f'Нельзя выставить тот же кошелёк, что и заказчик.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.executor_wallet = wallet
        order.save()
        return Response(
            {'success': f'Исполнитель {request.user.username} выставил кошелёк {wallet} для начисления средств по заказу \'{order}\'.'}
        )

    elif pay_and_delete is True and perms['can_pay_and_delete']:
        new_transaction = Transaction(order)
        if new_transaction.is_valid():
            try:
                new_transaction.commit()
                order.delete()
                return Response({'success': f'Транзакция проведена успешно! Заказ {order} удалён.'})
            except TransactionError as e:
                print(e)
                return Response({'detail': 'Транзакция провалилась. Вините разработчика.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': 'Слишком мало средств на кошельке заказчика.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    return Response({'detail': 'Нет подходящей операции или ошибка в запросе.'}, status=status.HTTP_400_BAD_REQUEST)
