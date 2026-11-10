# ==============================================================================
# Course: CITC-1301 Introduction to Programming & Logic
# Module: Direct Access File Processing (Chapter 6 Extension)
# File: direct_access_demo.py
# Description: Demonstrates file.seek(), file.tell(), fixed-width records,
#              and in-place record modification without copying the file.
# ==============================================================================

import os

FILENAME = "inventory_direct.txt"

# ------------------------------------------------------------------------------
# RECORD FORMAT SPECIFICATION (Fixed Width Text Approach)
# Field 1: Item ID   (6 characters)
# Field 2: Item Name (14 characters, left-justified, padded with spaces)
# Field 3: Quantity  (4 characters, right-justified)
# Field 4: Price     (7 characters, right-justified with 2 decimals)
# Delimiter: Line break '\n' (1 character)
# TOTAL FIXED RECORD SIZE: 6 + 14 + 4 + 7 + 1 = 32 bytes
# ------------------------------------------------------------------------------
RECORD_SIZE = 32


def create_fixed_width_file():
    """Creates a sample file where every single record is exactly 32 bytes."""
    print("--- 1. Creating Fixed-Width Records (32 bytes each) ---")

    records = [
        {"id": "A10001", "name": "USB Flash 64GB", "qty": 45, "price": 12.99},
        {"id": "A10002", "name": "Wireless Mouse", "qty": 80, "price": 19.50},
        {"id": "A10003", "name": "HDMI Cable 6ft", "qty": 120, "price": 8.75},
        {"id": "A10004", "name": "Mechanical KB",  "qty": 15, "price": 79.99},
        {"id": "A10005", "name": "Desk Pad XL",    "qty": 60, "price": 14.25},
    ]

    with open(FILENAME, "w") as f:
        for r in records:
            # Format each field to fit exact character widths
            formatted_record = (
                f"{r['id']:<6}"       # 6 chars
                f"{r['name']:<14}"    # 14 chars
                f"{r['qty']:>4}"      # 4 chars
                f"{r['price']:>7.2f}" # 7 chars
                f"\n"                 # 1 char
            )
            # Sanity check: Ensure each string is strictly 32 bytes
            assert len(formatted_record) == RECORD_SIZE, "Record size mismatch!"
            f.write(formatted_record)

    total_bytes = os.path.getsize(FILENAME)
    print(f"File created successfully. Total file size: {total_bytes} bytes.")
    print(f"Calculated records in file: {total_bytes // RECORD_SIZE} records.\n")


def direct_read_record(record_num):
    """
    Directly seeks to record_num (1-indexed) in O(1) time without reading
    earlier records.
    """
    print(f"--- 2. Direct Access Read: Record #{record_num} ---")

    # Byte offset formula: (Record Number - 1) * RECORD_SIZE
    byte_offset = (record_num - 1) * RECORD_SIZE

    try:
        with open(FILENAME, "r") as f:
            # Check file size to guard against reading past EOF
            f.seek(0, os.SEEK_END)
            total_size = f.tell()

            if byte_offset >= total_size or byte_offset < 0:
                raise IndexError(f"Record #{record_num} is out of bounds!")

            # 1. Reposition the file pointer directly to the target record
            f.seek(byte_offset)
            print(f"[POINTER] Jumped directly to byte offset: {f.tell()}")

            # 2. Read exactly one fixed-size record
            raw_record = f.read(RECORD_SIZE)
            print(f"[RAW BYTES]: '{raw_record.rstrip()}'")

            # 3. Slice fixed fields out of the fixed-width string
            item_id = raw_record[0:6].strip()
            item_name = raw_record[6:20].strip()
            qty = int(raw_record[20:24].strip())
            price = float(raw_record[24:31].strip())

            print(f"[PARSED RECORD] ID: {item_id} | Name: {item_name} | Qty: {qty} | Price: ${price:.2f}\n")

    except IndexError as err:
        print(f"[ERROR]: {err}\n")
    except FileNotFoundError:
        print(f"[ERROR]: File '{FILENAME}' not found.\n")


def update_record_in_place(record_num, new_qty, new_price):
    """
    Demonstrates in-place updating using mode 'r+'.
    Modifies record_num without creating a temporary file or rewriting other lines.
    """
    print(f"--- 3. In-Place Update: Modifying Record #{record_num} ---")
    byte_offset = (record_num - 1) * RECORD_SIZE

    # 'r+' allows simultaneous read and in-place write without truncating
    with open(FILENAME, "r+") as f:
        # 1. Seek to the record to inspect original data
        f.seek(byte_offset)
        existing = f.read(RECORD_SIZE)
        item_id = existing[0:6]
        item_name = existing[6:20]

        # 2. Assemble replacement record with identical byte footprint
        updated_record = (
            f"{item_id}"
            f"{item_name}"
            f"{new_qty:>4}"
            f"{new_price:>7.2f}"
            f"\n"
        )
        assert len(updated_record) == RECORD_SIZE

        # 3. Seek BACK to the beginning of this record offset before writing
        f.seek(byte_offset)
        f.write(updated_record)
        print(f"[UPDATED] Record #{record_num} updated in-place at byte {byte_offset}.\n")


def display_entire_file_with_pointer_tracking():
    """Demonstrates tell() advancing through the stream."""
    print("--- 4. Full File Inspection with file.tell() ---")
    with open(FILENAME, "r") as f:
        while True:
            current_pos = f.tell()
            line = f.readline()
            if line == "":
                break
            print(f"Byte {current_pos:03d} -> {line.rstrip()}")
    print()


def main():
    print("==========================================================")
    print("   CITC-1301: DIRECT ACCESS FILE PROCESSING DEMO          ")
    print("==========================================================")

    # Step 1: Write fixed-width records
    create_fixed_width_file()

    # Step 2: Jump straight to Record #4 without reading Records 1, 2, or 3
    direct_read_record(4)

    # Step 3: Jump straight to Record #2
    direct_read_record(2)

    # Step 4: Update Record #2 in place (e.g., sale updates qty to 75 and price to 17.99)
    update_record_in_place(record_num=2, new_qty=75, new_price=17.99)

    # Step 5: Read Record #2 back to prove it updated on disk
    direct_read_record(2)

    # Step 6: Show all records and their exact byte positions using tell()
    display_entire_file_with_pointer_tracking()


if __name__ == "__main__":
    main()
