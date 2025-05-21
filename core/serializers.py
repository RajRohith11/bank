from rest_framework import serializers
from .models import Customer, Account, Transaction

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone']

class AccountSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_type', 'balance', 'customer']
        read_only_fields = ['account_number']  # Prevents validation error on update

    def get_customer(self, obj):
        return {
            'name': obj.customer.name,
            'email': obj.customer.email,
            'phone': obj.customer.phone,
        }
    def update(self, instance, validated_data):
        customer_data = validated_data.pop('customer', None)
        if customer_data:
            # Check if the email is being changed
            if customer_data.get('email') != instance.customer.email:
                # If email has changed, ensure it's unique
                if Customer.objects.filter(email=customer_data.get('email')).exists():
                    raise serializers.ValidationError("Customer with this email already exists.")

            # Update customer fields
            for attr, value in customer_data.items():
                setattr(instance.customer, attr, value)
            instance.customer.save()

        # Update the account fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'transaction_type', 'amount', 'timestamp']
