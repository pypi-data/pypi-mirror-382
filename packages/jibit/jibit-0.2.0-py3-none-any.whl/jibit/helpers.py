from jibit.models import Card, Owner, IbanInfo


def parse_card_shaba_response(data: dict) -> Card:
    owners = [Owner(**o) for o in data["ibanInfo"]["owners"]]
    iban_info = IbanInfo(
        bank=data["ibanInfo"]["bank"],
        depositNumber=data["ibanInfo"]["depositNumber"],
        iban=data["ibanInfo"]["iban"],
        status=data["ibanInfo"]["status"],
        owners=owners
    )
    return Card(number=data["number"], type=data["type"], ibanInfo=iban_info)
