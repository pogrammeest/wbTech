from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

account_list = swagger_auto_schema(manual_parameters=[
    openapi.Parameter("ordering",
                      openapi.IN_QUERY,
                      description="Ordering of accounts",
                      type=openapi.TYPE_STRING, enum=['posts', '-posts']
                      )
])

feed_list = swagger_auto_schema(manual_parameters=[
    openapi.Parameter("read_only",
                      openapi.IN_QUERY,
                      description="Filter by re read only",
                      type=openapi.TYPE_STRING, enum=['true']
                      )
])

account_login = swagger_auto_schema(request_body=openapi.Schema(
    title=("Create post"),
    type=openapi.TYPE_OBJECT,
    required=['username', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description=('Username'), example=('username'),
                                   title='Name of user'
                                   ),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description=('password'),
                                   example=('asdgf12345'), title='Content', maxLength=128, minLength=1),
    }
)
)

post_swagger = swagger_auto_schema(request_body=openapi.Schema(
    title=("Create post"),
    type=openapi.TYPE_OBJECT,
    required=['title', 'content'],
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING, description=('Title of post'), example=('string'),
                                title='Title'
                                ),
        'content': openapi.Schema(type=openapi.TYPE_STRING, description=('Content of post'),
                                  example=('string'), title='Content'),
        'author_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                    description=('Author id, available only for staff user'),
                                    example=(1), title='Author id'),
    }
)
)
