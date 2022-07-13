from .models import User, Ability, Following
from graphene_django.types import DjangoObjectType
from graphql_auth import mutations
from graphql_auth.schema import UserQuery, MeQuery
import graphene



class AbilityObjectType(DjangoObjectType):
    class Meta:
        model = Ability
        fields = ['title', 'id']



class FollowingObjectType(DjangoObjectType):
    class Meta:
        model = Following
        fields = ['id', 'follower', 'created_at']



class UserObjectType(DjangoObjectType):
    class Meta:
        model = User
        fields = [
        'first_name', 'last_name', 'username', 'email',
            'photo', 'about', 'is_staff', 'is_superuser', 
                'is_author', 'premium_plans', 'intro_url', 'resume', 'abilities',
                    'payments', 'liked_posts', 'vieweds', 'user_comments', 'user_posts']



class Query(UserQuery, MeQuery, graphene.ObjectType):
    pass



class Mutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_change = mutations.PasswordChange.Field()
    archive_account = mutations.ArchiveAccount.Field()
    delete_account = mutations.DeleteAccount.Field()
    update_account = mutations.UpdateAccount.Field()
    send_secondary_email_activation = mutations.SendSecondaryEmailActivation.Field()
    verify_secondary_email = mutations.VerifySecondaryEmail.Field()
    swap_emails = mutations.SwapEmails.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
