from collections import UserDict
import re
import pickle
from datetime import datetime, timedelta
from TagNotes import Note
from Levenshtein import distance as levenshtein_distance

class Field:
    """Base class for entry fields."""
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Niepoprawny numer telefonu")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        pattern = re.compile(r"^\d{9}$")
        return pattern.match(value) is not None

class Email(Field):
    def __init__(self, value):
        if not self.validate_email(value):
            raise ValueError("Niepoprawny adres email")
        super().__init__(value)

    @staticmethod
    def validate_email(value):
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return pattern.match(value) is not None

class Birthday(Field):
    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Niepoprawna data urodzenia")
        super().__init__(value)

    @staticmethod
    def validate_birthday(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

class Address(Field):
    def __init__(self, street, city, postal_code, country):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        super().__init__(value=f"{street}, {city}, {postal_code}, {country}")

class Tag:
    def __init__(self, name):
        self.name = name

class Note(Field):
    pass

class Record:
    def __init__(self, name: Name, birthday: Birthday = None):
        self.id = None  # The ID will be assigned by AddressBook
        self.name = name
        self.phones = []
        self.emails = []
        self.birthday = birthday
        self.address = None  # Add a new property to store the address
        self.tags = []  # New property to store tags
        self.notes = []  # New property to store notes

    def add_address(self, address: Address):
        """Adds an address."""
        self.address = address

    def add_phone(self, phone: Phone):
        """Adds a phone number."""
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        """Removes a phone number."""
        self.phones.remove(phone)

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        """Changes a phone number."""
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_email(self, email: Email):
        """Adds an email address."""
        self.emails.append(email)

    def remove_email(self, email: Email):
        """Removes an email address."""
        self.emails.remove(email)

    def edit_email(self, old_email: Email, new_email: Email):
        """Changes an email address."""
        self.remove_email(old_email)
        self.add_email(new_email)

    def edit_name(self, new_name: Name):
        """Changes the first and last name."""
        self.name = new_name

    def add_tag(self, tag: Tag):
        self.tags.append(tag)

    def remove_tag(self, tag: Tag):
        self.tags.remove(tag)

    def add_note(self, note: Note):
        """Adds a note."""
        self.notes.append(note)

    def remove_note(self, note: Note):
        """Removes a note."""
        self.notes.remove(note)

    def edit_note(self, old_note: Note, new_note: Note):
        """Changes a note."""
        self.remove_note(old_note)
        self.add_note(new_note)

    def days_to_birthday(self):
        """Returns the number of days to the next birthday."""
        if not self.birthday or not self.birthday.value:
            return "Brak daty urodzenia"
        today = datetime.now()
        bday = datetime.strptime(self.birthday.value, "%Y-%m-%d")
        next_birthday = bday.replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        """Returns a string representation of the entry, including the ID."""
        tags = ', '.join(tag.name for tag in self.tags)
        phones = ', '.join(phone.value for phone in self.phones)
        emails = ', '.join(email.value for email in self.emails)
        birthday_str = f", Urodziny: {self.birthday.value}" if self.birthday else ""
        days_to_bday_str = f", Dni do urodzin: {self.days_to_birthday()}" if self.birthday else ""
        address_str = f"\nAdres: {self.address.value}" if self.address else ""
        notes_str = f"\nNotatki: {', '.join(note.value for note in self.notes)}" if self.notes else ""
        return f"ID: {self.id}, Imię i nazwisko: {self.name.value}, " \
               f"Telefony: {phones}, Email: {emails}{birthday_str}{days_to_bday_str}{address_str}, Tagi: {tags}{notes_str}"

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1
        self.free_ids = set()

    def add_record(self, record: Record):
        """Adds an entry to the address book with ID management."""
        while self.next_id in self.data or self.next_id in self.free_ids:
            self.next_id += 1
        if self.free_ids:
            record.id = min(self.free_ids)
            self.free_ids.remove(record.id)
        else:
            record.id = self.next_id
            self.next_id += 1
        self.data[record.id] = record
        print(f"Dodano wpis z ID: {record.id}.")

    def delete_record_by_id(self):
        """Deletes a record based on ID."""
        user_input = input("Podaj ID rekordu, który chcesz usunąć: ").strip()
        record_id_str = user_input.replace("ID: ", "").strip()

        try:
            record_id = int(record_id_str)
            if record_id in self.data:
                del self.data[record_id]
                self.free_ids.add(record_id)
                print(f"Usunięto rekord o ID: {record_id}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def find_record(self, search_term):
        """Finds entries containing the exact phrase provided."""
        found_records = []
        for record in self.data.values():
            if search_term.lower() in record.name.value.lower():
                found_records.append(record)
                continue
            for phone in record.phones:
                if search_term in phone.value:
                    found_records.append(record)
                    break
            for email in record.emails:
                if search_term in email.value:
                    found_records.append(record)
                    break
        return found_records

    def find_records_by_name(self, name):
        """Finds records that match the given name and surname."""
        matching_records = []
        for record_id, record in self.data.items():
            if name.lower() in record.name.value.lower():
                matching_records.append((record_id, record))
        return matching_records

    def delete_record(self):
        """Deletes the record based on the selected ID after searching by name."""
        name_to_delete = input("Podaj imię i nazwisko osoby, którą chcesz usunąć: ")
        matching_records = self.find_records_by_name(name_to_delete)

        if not matching_records:
            print("Nie znaleziono pasujących rekordów.")
            return

        print("Znaleziono następujące pasujące rekordy:")
        for record_id, record in matching_records:
            print(f"ID: {record_id}, Rekord: {record}")

        try:
            record_id_to_delete = int(input("Podaj ID rekordu, który chcesz usunąć: "))
            if record_id_to_delete in self.data:
                del self.data[record_id_to_delete]
                self.free_ids.add(record_id_to_delete)  # Add the ID back to the free ID pool
                print(f"Usunięto rekord o ID: {record_id_to_delete}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def show_all_records(self):
        """Displays all entries in the address book."""
        if not self.data:
            print("Książka adresowa jest pusta.")
            return
        for name, record in self.data.items():
            print(record)

    def __iter__(self):
        """Returns an iterator over the address book records."""
        self.current = 0
        return self

    def __next__(self):
        if self.current < len(self.data):
            records = list(self.data.values())[self.current:self.current+5]
            self.current += 5
            return records
        else:
            raise StopIteration

def suggest_correction_name(name_to_edit, matching_records):
    closest_name = min(matching_records, key=lambda x: levenshtein_distance(name_to_edit, x[1].name.value))
    return closest_name[1].name.value

def edit_record(book):
    """Edits an existing record in the address book."""
    name_to_edit = input("Wprowadź imię i nazwisko, które chcesz edytować: ")
    matching_records = book.find_records_by_name(name_to_edit)

    if not matching_records:
        print("Nie znaleziono pasujących rekordów.")
        return

    if len(matching_records) > 1:
        print("Znaleziono więcej niż jeden pasujący rekord. Proszę wybrać jeden z poniższych:")
        for idx, (record_id, record) in enumerate(matching_records, start=1):
            print(f"{idx}. ID: {record_id}, Rekord: {record}")

        try:
            choice_idx = int(input("Wybierz numer rekordu do edycji: "))
            if 0 < choice_idx <= len(matching_records):
                record_id, record = matching_records[choice_idx - 1]
            else:
                print("Nieprawidłowy numer rekordu.")
                return
        except ValueError:
            print("Nieprawidłowa wartość. Wprowadź numer.")
            return
    else:
        record_id, record = matching_records[0]

    print(f"Edytowanie: ID: {record_id}, {name_to_edit}.")

    # Sugestia poprawek dla imienia i nazwiska
    closest_name = suggest_correction_name(name_to_edit, matching_records)
    print(f"Czy chodziło Ci o: {closest_name} - dla imienia i nazwiska?")

    new_name_input = input("Podaj nowe imię i nazwisko (wciśnij Enter, aby zachować obecne): ")
    if new_name_input.strip():
        record.edit_name(Name(new_name_input))
        print("Zaktualizowano imię i nazwisko.")

    # Edycja numerów telefonów
    if record.phones:
        print("Obecne numery telefonów: ")
        for idx, phone in enumerate(record.phones, start=1):
            print(f"{idx}. {phone.value}")
        phone_to_edit = input("Podaj numer telefonu do edycji (wciśnij Enter, aby zachować obecny): ")
        if phone_to_edit.strip():
            try:
                idx = int(phone_to_edit) - 1
                if 0 <= idx < len(record.phones):
                    new_phone_number = input("Podaj nowy numer telefonu: ")
                    record.edit_phone(record.phones[idx], Phone(new_phone_number))
                    print("Numer telefonu zaktualizowany.")
                else:
                    print("Niepoprawny indeks numeru.")
            except ValueError:
                print("Nieprawidłowa wartość. Wprowadź numer.")
    else:
        print("Brak numerów telefonu do edycji.")

    # Edycja adresów e-mail
    if record.emails:
        print("Obecne adresy e-mail: ")
        for idx, email in enumerate(record.emails, start=1):
            print(f"{idx}. {email.value}")
        email_to_edit = input("Podaj adres e-mail do edycji (wciśnij Enter, aby zachować obecny): ")
        if email_to_edit.strip():
            try:
                idx = int(email_to_edit) - 1
                if 0 <= idx < len(record.emails):
                    new_email_address = input("Podaj nowy adres e-mail: ")
                    record.edit_email(record.emails[idx], Email(new_email_address))
                    print("Adres e-mail zaktualizowany.")
                else:
                    print("Niepoprawny indeks adresu e-mail.")
            except ValueError:
                print("Nieprawidłowa wartość. Wprowadź numer.")
    else:
        print("Brak adresów e-mail do edycji.")

    # Edycja daty urodzenia
    if record.birthday:
        print(f"Obecna data urodzenia: {record.birthday.value}")
        new_birthday = input("Podaj nową datę urodzenia w formacie YYYY-MM-DD (wciśnij Enter, aby zachować obecną): ")
        if new_birthday.strip():
            try:
                record.birthday = Birthday(new_birthday)
                print("Data urodzenia zaktualizowana.")
            except ValueError as e:
                print(f"Błąd: {e}")
    else:
        print("Brak daty urodzenia do edycji.")

    # Edycja adresu
    if record.address:
        print(f"Obecny adres: {record.address.value}")
        new_street = input("Podaj nową ulicę (wciśnij Enter, aby zachować obecną): ")
        new_city = input("Podaj nowe miasto (wciśnij Enter, aby zachować obecne): ")
        new_postal_code = input("Podaj nowy kod pocztowy (wciśnij Enter, aby zachować obecny): ")
        new_country = input("Podaj nowy kraj (wciśnij Enter, aby zachować obecny): ")
        if new_street.strip() or new_city.strip() or new_postal_code.strip() or new_country.strip():
            new_address = Address(
                street=new_street if new_street.strip() else record.address.street,
                city=new_city if new_city.strip() else record.address.city,
                postal_code=new_postal_code if new_postal_code.strip() else record.address.postal_code,
                country=new_country if new_country.strip() else record.address.country
            )
            record.add_address(new_address)
            print("Adres zaktualizowany.")
    else:
        print("Brak adresu do edycji.")

    # Edycja tagów
    if record.tags:
        print("Obecne tagi: ")
        for idx, tag in enumerate(record.tags, start=1):
            print(f"{idx}. {tag.name}")
        tag_to_edit = input("Podaj tag do edycji (wciśnij Enter, aby zachować obecny): ")
        if tag_to_edit.strip():
            try:
                idx = int(tag_to_edit) - 1
                if 0 <= idx < len(record.tags):
                    new_tag_name = input("Podaj nową nazwę tagu: ")
                    record.tags[idx].name = new_tag_name
                    print("Tag zaktualizowany.")
                else:
                    print("Niepoprawny indeks tagu.")
            except ValueError:
                print("Nieprawidłowa wartość. Wprowadź numer.")
    else:
        print("Brak tagów do edycji.")

    # Edycja notatek
    if record.notes:
        print("Obecne notatki: ")
        for idx, note in enumerate(record.notes, start=1):
            print(f"{idx}. {note.value}")
        note_to_edit = input("Podaj notatkę do edycji (wciśnij Enter, aby zachować obecną): ")
        if note_to_edit.strip():
            try:
                idx = int(note_to_edit) - 1
                if 0 <= idx < len(record.notes):
                    new_note_text = input("Podaj nową treść notatki: ")
                    record.notes[idx].value = new_note_text
                    print("Notatka zaktualizowana.")
                else:
                    print("Niepoprawny indeks notatki.")
            except ValueError:
                print("Nieprawidłowa wartość. Wprowadź numer.")
    else:
        print("Brak notatek do edycji.")

    print("Edycja zakończona pomyślnie.")

def main():
    book = AddressBook()
    try:
        with open("address_book.pickle", "rb") as file:
            book = pickle.load(file)
            print("Wczytano dane z poprzedniej sesji.")
    except FileNotFoundError:
        print("Brak pliku z danymi. Rozpoczynanie nowej książki adresowej.")

    while True:
        print("\n=== Książka Adresowa ===")
        print("1. Dodaj wpis")
        print("2. Edytuj wpis")
        print("3. Usuń wpis")
        print("4. Szukaj wpisu")
        print("5. Wyświetl wszystkie wpisy")
        print("6. Zapisz i wyjdź")

        choice = input("Wybierz opcję (wpisz numer): ")
        if choice == "1":
            try:
                record = create_record()
                book.add_record(record)
            except ValueError as e:
                print(f"Błąd: {e}")
        elif choice == "2":
            edit_record(book)
        elif choice == "3":
            book.delete_record()
        elif choice == "4":
            search_term = input("Wprowadź frazę do wyszukania: ")
            found_records = book.find_record(search_term)
            if found_records:
                print("Znalezione rekordy:")
                for record in found_records:
                    print(record)
            else:
                print("Nie znaleziono pasujących rekordów.")
        elif choice == "5":
            book.show_all_records()
        elif choice == "6":
            with open("address_book.pickle", "wb") as file:
                pickle.dump(book, file)
                print("Zapisano dane. Do widzenia!")
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
