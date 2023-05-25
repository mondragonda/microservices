import strawberry
import datetime


@strawberry.federation.type(keys=["id"], description="User register information.")
class User:
    id: strawberry.ID
    email: str
    password: strawberry.Private[str]
    photo_url: str
    first_name: str
    last_name: str
    date_of_birth: datetime.date
    address: str

    def __init__(self, id: strawberry.ID, email: str, photo_url: str, first_name: str, last_name: str, date_of_birth: datetime.date, address: str):
        self.id = id
        self.email = email
        self.photo_url = photo_url
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.address = address


schema = strawberry.federation.Schema(
    Query,
    Mutation,
    enable_federation_2=True,
)
