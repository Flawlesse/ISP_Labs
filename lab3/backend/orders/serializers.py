from decimal import Decimal
from proj_helpers.order_perms import get_permissions_for_order
from rest_framework import serializers
from .models import Account, Order, Wallet
from proj_helpers.wallet_password import encrypt, check_pass
from proj_helpers.custom_validators import password_validator


# -----------------ACCOUNT SERIALIZERS----------------------
class AccountDisplaySerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    current_order = serializers.StringRelatedField()
    wallets = serializers.StringRelatedField(many=True)

    class Meta:
        model = Account
        fields = (
            'username', 'is_admin', 'can_edit', 'first_name',
            'last_name', 'email', 'phone_number',
            'about', 'profile_pic', 'orders_executed',
            'current_order', 'wallets',
        )

    def get_is_admin(self, obj):
        return obj.is_superuser

    def get_can_edit(self, obj):
        return self.context['request'].user.username == obj.username


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'username', 'first_name',
            'last_name', 'email', 'phone_number',
            'about', 'profile_pic',
        )


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, validators=[password_validator])
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = Account
        fields = (
            'username', 'first_name',
            'last_name', 'email', 'phone_number',
            'password', 'password2',
            'about', 'profile_pic',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}, 'validators': [password_validator]}
        }

    def get_validation_exclusions(self):
        exclusions = super().get_validation_exclusions()
        return exclusions + ['profile_pic']

    def save(self):
        account = Account(
            username=self.validated_data.get('username'),
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
            email=self.validated_data.get('email'),
            phone_number=self.validated_data.get('phone_number'),
            about=self.validated_data.get('about'),
            profile_pic=self.validated_data.get('profile_pic'),
        )
        password = self.validated_data.get('password')
        password2 = self.validated_data.get('password2')
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Пароли не совпадают!'})
        account.set_password(password2)
        account.save()
        return account


# -----------------ORDER SERIALIZERS-----------------------
class OrderSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    executor = serializers.StringRelatedField()
    orderer_wallet = serializers.StringRelatedField()
    executor_wallet = serializers.StringRelatedField()

    order_state = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_accept = serializers.SerializerMethodField()
    can_reject = serializers.SerializerMethodField()
    can_pick_ord_wallet = serializers.SerializerMethodField()
    can_pick_exec_wallet = serializers.SerializerMethodField()
    can_pay_and_delete = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'author', 'executor', 'title', 'date_posted',
            'description', 'price', 'orderer_wallet',
            'executor_wallet', 'order_state',
            'can_edit', 'can_accept', 'can_reject',
            'can_pick_ord_wallet', 'can_pick_exec_wallet',
            'can_pay_and_delete',
        )
        extra_kwargs = {
            'date_posted': {'read_only': True},
            'orderer_wallet': {'read_only': True},
            'executor_wallet': {'read_only': True},
            'order_state': {'read_only': True},
        }

    def get_order_state(self, order):
        return str(order.get_state())

    def get_can_edit(self, order):
        return get_permissions_for_order(order, self.context['request'])['can_edit']

    def get_can_accept(self, order):
        return get_permissions_for_order(order, self.context['request'])['can_accept']

    def get_can_reject(self, order):
        return get_permissions_for_order(order, self.context['request'])['can_reject']

    def get_can_pick_ord_wallet(self, order):
        return get_permissions_for_order(order, self.context['request'])['can_pick_ord_wallet']

    def get_can_pick_exec_wallet(self, order):
        return get_permissions_for_order(order, self.context['request'])['can_pick_exec_wallet']

    def get_can_pay_and_delete(self, order):
        return get_permissions_for_order(order, self.context['request'])['can_pay_and_delete']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return Order.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


# -----------------WALLET SERIALIZERS----------------------
class WalletCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'},
        validators=[password_validator]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Repeat password'},
        validators=[password_validator]
    )

    class Meta:
        model = Wallet
        fields = (
            'name', 'password', 'password2',
            'money'
        )
        extra_kwargs = {
            'money': {'default': Decimal('100.00')}
        }

    def save(self):
        wallet = Wallet(
            name=self.validated_data['name'],
            money=self.validated_data['money'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Пароли не совпадают!'})

        enc_string = encrypt(password)
        wallet.password = enc_string
        wallet.save()
        return wallet


class WalletUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('name', 'money')


class WalletDisplaySerializer(serializers.ModelSerializer):
    accounts = serializers.StringRelatedField(many=True)

    class Meta:
        model = Wallet
        fields = ('name', 'money', 'accounts')


class WalletAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('name', 'password', )
        extra_kwargs = {
            'password': {'write_only': True, 'read_only': False, 'validators': [password_validator]},
            'name': {'validators': []}
        }

    def validate_name(self, name):
        if not Wallet.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                "Не существует кошелька с данными именем.")
        return name

    def validate_password(self, password):
        wallet = Wallet.objects.get(name=self.initial_data['name'].strip())
        enc_password = wallet.password
        if not check_pass(password, enc_password):
            raise serializers.ValidationError("Неверный пароль.")
        return password

    def get_wallet(self):
        if self.is_valid():
            return Wallet.objects.get(name=self.data['name'])
        return None
