class User:
    def __init__(self, email: str, role: str, organizationId: str):
        self.id = email
        self.email = email
        self.role = role
        self.organizationId = organizationId
