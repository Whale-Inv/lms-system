import requests

from config import settings


class StripeService:
    """
        Класс для работы с Stripe API
    """

    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.base_url = 'https://api.stripe.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def create_product(self, name, description=None, metadata=None):
        """
            Создание продукта в Stripe
        """
        data = {'name': name}
        if description:
            data['description'] = description
        if metadata:
            for key, value in metadata.items():
                data[f'metadata[{key}]'] = str(value)

        response = requests.post(
            f'{self.base_url}/products',
            headers=self.headers,
            data=data
        )
        return response.json()

    def create_price(self, product_id, unit_amount, currency='usd'):
        """
            Создание цены для продукта (одноразовый платеж)
        """
        data = {
            'product': product_id,
            'currency': currency,
            'unit_amount': unit_amount,
        }

        response = requests.post(
            f'{self.base_url}/prices',
            headers=self.headers,
            data=data
        )
        return response.json()

    def create_checkout_session(self, price_id, success_url, cancel_url, quantity=1, metadata=None):
        """
            Создание сессии оплаты по существующей цене
        """
        data = {
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items[0][price]': price_id,
            'line_items[0][quantity]': quantity,
        }

        if metadata:
            for key, value in metadata.items():
                data[f'metadata[{key}]'] = str(value)

        response = requests.post(
            f'{self.base_url}/checkout/sessions',
            headers=self.headers,
            data=data
        )
        return response.json()

    def retrieve_checkout_session(self, session_id):
        """
            Получение информации о сессии оплаты
        """
        response = requests.get(
            f'{self.base_url}/checkout/sessions/{session_id}',
            headers=self.headers
        )
        return response.json()

    def create_full_payment_flow(self, product_name, amount, success_url, cancel_url,
                                 product_description=None, currency='usd', metadata=None):
        """
            Полный процесс: создает продукт, цену и сессию за один вызов
            (для случаев, когда нужно создать новый продукт)
        """
        # 1. Создаем продукт
        product = self.create_product(
            name=product_name,
            description=product_description,
            metadata={'type': 'course'}
        )

        # 2. Создаем цену
        unit_amount = int(amount * 100)
        price = self.create_price(
            product_id=product['id'],
            unit_amount=unit_amount,
            currency=currency
        )

        # 3. Создаем сессию
        session = self.create_checkout_session(
            price_id=price['id'],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )

        return {
            'product': product,
            'price': price,
            'session': session,
            'checkout_url': session['url']
        }

stripe_service = StripeService()
