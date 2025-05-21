from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Account, Transaction
from .serializers import CustomerSerializer, AccountSerializer, TransactionSerializer
from decimal import Decimal
# 
@api_view(['POST'])
def create_customer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_customers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_account(request):
    customer_id = request.data.get('customer_id')
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    account = Account.objects.create(
        account_number=request.data['account_number'],
        account_type=request.data['account_type'],
        balance=request.data['balance'],
        customer=customer
    )
    serializer = AccountSerializer(account)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_account_by_number(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
        serializer = AccountSerializer(account)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_account(request, account_number):
    print("➡️ PUT request received for account:", account_number)
    print("📦 Incoming data:", request.data)

    try:
        account = Account.objects.get(account_number=account_number)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AccountSerializer(account, data=request.data)
    if serializer.is_valid():
        serializer.save()
        print("✅ Account updated successfully")
        return Response(serializer.data)
    
    print("❌ Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def deposit(request):
    account_number = request.data.get('account_number')
    amount = float(request.data.get('amount'))
    try:
        amount =Decimal(amount)
        account = Account.objects.get(account_number=account_number)
        account.balance += amount
        account.save()
        Transaction.objects.create(account=account, transaction_type='deposit', amount=amount)
        return Response({'message': 'Deposit successful'}, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def withdraw(request):
    account_number = request.data.get('account_number')
    amount = float(request.data.get('amount'))
    try:
        amount = Decimal(amount)
        account = Account.objects.get(account_number=account_number)
        if account.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        account.balance -= amount
        account.save()
        Transaction.objects.create(account=account, transaction_type='withdraw', amount=amount)
        return Response({'message': 'Withdrawal successful'}, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .models import Account, Transaction
from rest_framework.exceptions import NotFound 

@api_view(['GET'])
def get_account_by_number(request, account_number):
    try:
        
        account = Account.objects.get(account_number=account_number)
        
        
        serializer = AccountSerializer(account)
        
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        raise NotFound(f"Account with account number {account_number} not found.")
    

@api_view(['GET'])
def get_all_accounts(request):
    
    accounts = Account.objects.all()
    

    serializer = AccountSerializer(accounts, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['POST'])
def transfer(request):
    source_account_number = request.data.get('source_account_number')
    destination_account_number = request.data.get('destination_account_number')
    amount = request.data.get('amount')

    try:
        amount = Decimal(amount)
        source_account = Account.objects.get(account_number=source_account_number)
        destination_account = Account.objects.get(account_number=destination_account_number)

        if source_account.balance < amount:
            return Response({'error': 'Insufficient balance in source account'}, status=status.HTTP_400_BAD_REQUEST)

        source_account.balance -= amount
        destination_account.balance += amount
        source_account.save()
        destination_account.save()

        Transaction.objects.create(account=source_account, transaction_type='transfer-out', amount=amount)
        Transaction.objects.create(account=destination_account, transaction_type='transfer-in', amount=amount)

        return Response({'message': 'Transfer successful'}, status=status.HTTP_200_OK)

    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Invalid amount format'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def transaction_history(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_account(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
        account.delete()
        return Response({'message': 'Account deleted successfully'})
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
