from django.shortcuts import get_object_or_404
from graphene_django import DjangoObjectType
from .models import Payment, PremiumPlan
import graphene
from zeep.client import Client
from django.conf import settings
import logging


zarinpal = getattr(settings, 'ZARINPAL', None)
client = Client(zarinpal['sandbox']['request_url'])



class PremiumPlanObjectType(DjangoObjectType):
    class Meta:
        model = PremiumPlan
        fields = ['id', 'user', 'description', 'amount', 
                                    'started_date', 'finished_date']



class PaymentObjectType(DjangoObjectType):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'plan', 'amount', 'status', 'authority', 
                        'ref_id', 'card_pan', 'card_hash', 'date_created']



class ResultRequestObjectType(graphene.ObjectType):
    payment = graphene.Field(PaymentObjectType)
    startpay_link = graphene.String()


class PaymentRequestMutation(graphene.Mutation):
    class Arguments:
        amount = graphene.Float()

    information_need = graphene.Field(ResultRequestObjectType)
    register_url = graphene.String()


    def mutate(root, info, amount):
        if info.context.user.is_authenticated:
            result = client.service.PaymentRequest(
                zarinpal['merchant_id'],
                amount,
                "Premium Plan for our website",
                info.context.user.email,
                '09123456789',
                zarinpal['callback_url']
            )
            if result.Status == 100:
                payment = Payment.objects.create(
                    amount=amount,
                    user=info.context.user,
                    authority=result.Authority
                )
                information_need = {
                    'payment': payment,
                    'startpay_link': zarinpal['sandbox']['startpay_url'].format(
                        result.Authority
                    )
                }
                return PaymentRequestMutation(
                    information_need=information_need
                )
            logging.error(result)
        return PaymentRequestMutation(register_url='http://locahost/register')



class PaymentVerifyMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int()


    payment = graphene.Field(PaymentObjectType)


    def mutate(root, info, id):
        p = get_object_or_404(Payment, pk=id, 
                            user=info.context.user)
        result = client.service.PaymentVerification(
            zarinpal['merchant_id'],
            p.authority,
            p.amount
        )
        if result.Status == 100 or result.Status == 101:
            plan = PremiumPlan.objects.create(user=info.context.user)
            plan.set_finish_date()
            p.status = 'S'
            p.ref_id = result.RefID
            p.save()
            return PaymentVerifyMutation(payment=p)
        p.status = 'F'
        p.ref_id = result.RefID
        p.save()
        return PaymentVerifyMutation(payment=p)



class Mutation(graphene.ObjectType):
    payment_request_mutation = PaymentRequestMutation.Field()
    payment_verify_mutation = PaymentVerifyMutation.Field()



class Query(graphene.ObjectType):
    my_payment = graphene.Field(PaymentObjectType, username=graphene.String())
    my_premium_plan = graphene.Field(PremiumPlanObjectType, username=graphene.String())

    def resolve_my_payment(root, info, username):
        return get_object_or_404(Payment, user__username=username)

    def resolve_my_premium_plan(root, info, username):
        return get_object_or_404(PremiumPlan, user__username=username)



schema = graphene.Schema(query=Query, mutation=Mutation)
