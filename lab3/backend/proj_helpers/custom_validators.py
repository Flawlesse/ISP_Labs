from django.core.validators import RegexValidator


name_validator = RegexValidator(
    regex=r'^[A-Za-z0-9_\-]{4,40}$',
    message="Ошибка в имени пользователя. От 4 до 40 символов. " +
            "Допустимы исключительно латинские буквы, цифры и '_-'."
)


phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Ошибка в номере телефона. Формат: [+][1]999999999." +
            "От 9 до 15 цифр, не считая '+' и '1' в самом начале."
)


password_validator = RegexValidator(
    regex=r'^[A-Za-z0-9#\'\"!@#$%^&*()_\\|\-=+:;?<>\[\]{},.]{8,60}$',
    message="Введите пароль от 8 до 60 символов. Используйте " +
            "латиницу, цифры и спецсимволы на клавиатуре."
)
