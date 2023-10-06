from collections import UserDict
from datetime import datetime
import json


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)


class Name(Field):
    @Field.value.setter
    def value(self, name):
        self._value = name


class Phone(Field):
    @Field.value.setter
    def value(self, phone):
        if len(phone) != 10 or not phone.isdigit():
            raise ValueError('Enter correct phone')
        self._value = phone


class Birthday(Field):  # Тут birthday це об'єкт datetime
    @Field.value.setter
    def value(self, birthday):
        if isinstance(birthday, datetime):
            self._value = birthday
        else:
            raise ValueError('Enter correct birthday')


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = birthday  # Тут birthday це екземпляр класу Birthday

    def add_phone(self, phone):
        valid_phone = Phone(phone)
        if valid_phone.value is not None:
            self.phones.append(valid_phone)
        else:
            return 'Phone is not valid'

    def remove_phone(self, phone):
        valid_phone = Phone(phone)
        phone_to_remove = None
        for ph in self.phones:
            if ph.value == valid_phone.value:
                phone_to_remove = ph
                break
        if phone_to_remove is not None:
            self.phones.remove(phone_to_remove)
        else:
            return 'This contact don`t have this phone'

    def edit_phone(self, old_phone_value, new_phone_value):
        old_phone_index = None
        for i, ph in enumerate(self.phones):
            if ph.value == old_phone_value:
                old_phone_index = i
                break
        if old_phone_index is not None:
            new_phone = Phone(new_phone_value)
            if new_phone.value is not None:
                self.phones[old_phone_index] = new_phone
            else:
                return 'New phone is not valid'
        else:
            raise ValueError('Phone not found')

    def find_phone(self, phone):
        valid_phone = Phone(phone)
        for ph in self.phones:
            if ph.value == valid_phone.value:
                return ph
        return None

    def days_to_birthday(self):
        if self.birthday:
            today_day = datetime.today()
            current_year = today_day.year
            contact_birthday = self.birthday.value
            contact_birthday = contact_birthday.replace(year=current_year)
            if contact_birthday < today_day:
                contact_birthday = contact_birthday.replace(year=current_year + 1)
            result = contact_birthday - today_day
            return result.days
        else:
            return 'No birthday info for this contact'

    def __str__(self):
        name_str = f"Contact name: {self.name.value}"
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%Y-%m-%d')}" if self.birthday else (", birthday:"
                                                                                                        " no info")
        return f"{name_str}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        if isinstance(record, Record):
            self.data[record.name.value] = record
        else:
            raise ValueError("Here you can add only records")

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            print(f"This contact don`t exist")

    def iterator(self, n):
        index = 0
        not_fitting = len(self.data) % n
        while index < len(self.data):
            try:
                yield dict(list(self.data.items())[index:index + n])
                index += n
            except IndexError:
                yield dict(list(self.data.items())[index:index + not_fitting])

    def find_contacts(self, message: str):
        result = []
        for contact in self.data.values():
            for phone in contact.phones:
                if phone.value.find(message) != -1:
                    result.append(str(contact))
            if contact.name.value.find(message) != -1:
                result.append(str(contact))
        return result if result else 'No info found'

    def save_to_file(self, filename: str):
        records_to_save = []
        for contact in self.data.values():
            record_data = {
                "name": contact.name.value,
                "phones": [phone.value for phone in contact.phones],
                "birthday": None
            }
            if contact.birthday:
                record_data["birthday"] = contact.birthday.value.strftime("%Y-%m-%d")
            records_to_save.append(record_data)
        with open(filename, 'w') as f:
            json.dump(records_to_save, f)

    @classmethod
    def load_from_file(cls, filename: str):
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
        unloaded_address_book = cls()
        for record_data in loaded_data:
            name = record_data["name"]
            phones = record_data["phones"]
            birthday_str = record_data["birthday"]
            if birthday_str:
                birthday = Birthday(datetime.strptime(birthday_str, "%Y-%m-%d"))
            else:
                birthday = None
            contact = Record(name, birthday)
            for phone in phones:
                contact.add_phone(phone)
            unloaded_address_book.add_record(contact)
        return unloaded_address_book


record = Record('Anton')
record.add_phone('0964784877')
record.birthday = Birthday(datetime(year=1990, month=10, day=10))
address_book = AddressBook()
address_book.add_record(record)
address_book.save_to_file('address_book.json')
unpacked_address_book = address_book.load_from_file('address_book.json')
unpacked_record = unpacked_address_book['Anton']
print(unpacked_record.name.value)
print(unpacked_record.phones[0].value)
print(unpacked_record.birthday)
print(address_book.find_contacts('ton'))
