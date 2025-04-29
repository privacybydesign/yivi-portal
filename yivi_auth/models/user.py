class User:
    def __init__(self, email: str, role: str, organizationSlug: str):
        self.id = email
        self.email = email
        self.role = role
        self.organizationSlug = organizationSlug
