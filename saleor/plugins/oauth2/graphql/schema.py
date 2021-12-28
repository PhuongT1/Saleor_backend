import graphene

from ....graphql.core.federation import build_federated_schema
from .mutations import SocialLogin, SocialLoginConfirm  # , AccountRegisterSocial


class Queries(graphene.ObjectType):
    author = graphene.String(default_value="wecre8")


class Mutations(graphene.ObjectType):
    social_login = SocialLogin.Field()
    social_login_confirm = SocialLoginConfirm.Field()
    # account_register_social = AccountRegisterSocial.Field()


schema = build_federated_schema(query=Queries, mutation=Mutations)
