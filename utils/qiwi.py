import datetime
import uuid
from dataclasses import dataclass
from datetime import datetime

import pyqiwi

qiwi_wallet = "+999999999"
qiwi_pub = "knajsnasklda"
qiwi_token = "lasjasuasjsd"

wallet = pyqiwi.Wallet(token=qiwi_token, number=qiwi_wallet)


class NotEnoughMoney(Exception):
    pass


class NoPaymentFound(Exception):
    pass


@dataclass
class Payment:
    amount: int
    id: str = None

    def create(self):
        self.id = str(uuid.uuid4())

    def check_payment(self):
        start_date = datetime.datetime.now() - datetime.timedelta(days=2)
        transactions = wallet.history(
            start_date=start_date).get("transactions")

        for transaction in transactions:
            if transaction.comment:
                if str(self.id) in transaction.comment:
                    if float(transaction.total.amount) >= float(self.amount):
                        return True
                    else:
                        raise NotEnoughMoney
        else:
            raise NoPaymentFound

    @property
    def link(self):
        link = "https://oplata.qiwi.com/create?publicKey={pubkey}&amount={amount}&comment={comment}"
        return link.format(pubkey=qiwi_pub, amount=self.amount, comment=self.id)
