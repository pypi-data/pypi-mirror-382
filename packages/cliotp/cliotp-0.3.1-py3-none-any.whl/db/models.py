from django.db import models

from crypto import Crypto
from manage import init_django

init_django()


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Group(BaseModel):
    name = models.CharField(max_length=200)
    salt = models.BinaryField(max_length=32)


class Account(models.Model):
    SHA1 = "0"
    SHA256 = "1"
    SHA512 = "2"

    ALGORITHM_CHOICES = {
        SHA1: "sha1",
        SHA256: "sha256",
        SHA512: "sha512",
    }

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    service = models.CharField(max_length=200)
    encrypted_seed = models.BinaryField(max_length=64)
    initialization_vector = models.BinaryField(max_length=32)
    period = models.IntegerField(default=30)
    digits = models.IntegerField(default=6)
    algorithm = models.CharField(
        max_length=10,
        choices=ALGORITHM_CHOICES,
        default=SHA1,
    )

    @property
    def seed(self):
        crypto = Crypto(self)
        return crypto.decrypt(self.encrypted_seed)

    @seed.setter
    def seed(self, plaintext):
        crypto = Crypto(self)
        self.encrypted_seed = crypto.encrypt(plaintext)
        return self.encrypted_seed

    def get_algorithm(self):
        return self.get_algorithm_display()

    def tags(self):
        account_tags = self.tag_set.all()
        return ", ".join([tag.name for tag in account_tags])


class Tag(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    account = models.ManyToManyField(Account)
    name = models.CharField(max_length=200)
