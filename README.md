# CITC-1301: Introduction to Programming & Logic
## Supplementary Module: Direct (Random) Access File Processing
**Textbook Context:** Extension to Tony Gaddis, *Starting Out with Python* (Chapter 6, Slide 7)  
**Duration:** 50–75 Minutes (1 Class Session or Lab Lab/Lecture Split)  
**Prerequisites:** Chapter 6 core concepts (file modes `'r'`, `'w'`, sequential `readline()`, and context managers).

---

## 1. Lesson Objectives & Pedagogical Overview

By the end of this module, students will be able to:
1. **Differentiate** between sequential access and direct (random) access at the storage layer.
2. **Explain** how the OS file pointer behaves and inspect its position using `file.tell()`.
3. **Reposition** the file pointer instantaneously using `file.seek(offset, whence)`.
4. **Calculate** byte offsets for fixed-width records using basic algebraic formulas:
   $$\text{Offset} = (\text{Record Index} - 1) \times \text{Fixed Record Size}$$
5. **Update and read** records in place without rewriting or copying the entire file.

---

## 2. Conceptual Background & Teaching Narrative

### The Problem with Sequential Access
"In Chapter 6, we processed files sequentially: to find the 500th employee in a file of 1,000 records, our program had to read lines 1 through 499 first. Modifying employee #500 required copying the entire file into a temporary file, writing the modified line, and renaming it. 

Imagine an ATM system or an inventory lookup doing that with 10 million bank accounts. It would be intolerably slow and disk-intensive.

### The Direct Access Solution
Direct access treats a file like an array or an indexed street address. By enforcing a **fixed record size**, we know the exact byte position where any record begins and ends. We jump directly there in $\mathcal{O}(1)$ constant time."

---

## 3. Core Mechanics & API

| Method / Mode | Purpose & Behavior |
| :--- | :--- |
| **`file.tell()`** | Returns an integer indicating the current byte position of the file pointer. |
| **`file.seek(offset, whence)`** | Repositions the file pointer to `offset` bytes relative to `whence`. |
| **`whence = 0`** (`os.SEEK_SET`) | Default. Relative to the **beginning** of the file (`offset >= 0`). |
| **`whence = 1`** (`os.SEEK_CUR`) | Relative to the **current** pointer position. |
| **`whence = 2`** (`os.SEEK_END`) | Relative to the **end** of the file (used with binary modes). |
| **Mode `'r+'` / `'rb+'`** | Opens a file for **both reading and in-place updating** without truncating it. |

---

## 4. In-Class Live-Coding Script: `direct_access_demo.py`

This standalone script demonstrates fixed-length record construction, instant jumping, in-place record modification, and error checking.

```python
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
```

---

## 5. Classroom Step-by-Step Delivery Guide

### Phase 1: Motivation & Visualizing Byte Offsets (15 min)
1. **Whiteboard Diagram:** Draw a byte tape on the board:
   ```text
   [ Byte 0 .. 31 ] -> Record 1 (Cindy)
   [ Byte 32 .. 63] -> Record 2 (Marcus)
   [ Byte 64 .. 95] -> Record 3 (Elena)
   ```
2. **Derive the Formula with Students:**
   * Ask: *"If each record is 32 bytes, where does Record 1 start?"* $\rightarrow 0$.
   * Ask: *"Where does Record 2 start?"* $\rightarrow 32$.
   * Ask: *"Where does Record $N$ start?"* $\rightarrow (N - 1) \times 32$.
3. **Contrast with Variable Length:** Explain why direct access fails if names are variable lengths (e.g., `'Al'` vs `'Christopher'`) unless padded.

### Phase 2: Live-Coding the Fixed-Width Setup (15 min)
1. Write `create_fixed_width_file()`.
2. Emphasize format specifiers: `{name:<14}` forces left alignment and pads remaining spaces up to 14 characters.
3. Run the script and show `os.path.getsize(FILENAME)`. Verify that $5 \times 32 = 160$ bytes.

### Phase 3: The Magic of `seek()` and `tell()` (15 min)
1. Un-comment `direct_read_record(4)`.
2. Step through `f.seek(byte_offset)`. Point out to students that line 1, line 2, and line 3 were **never read into RAM**.
3. Point out `f.tell()` in the console output to show how the pointer advances.

### Phase 4: In-Place Modification with `'r+'` (15 min)
1. Remind students: in sequential files, editing record #2 requires rewriting the whole file.
2. Introduce `'r+'` (Read + Write without wiping).
3. Demonstrate the **"Seek-Back" rule**:
   * Reading advances the pointer by 32 bytes.
   * To overwrite that same record, you must call `f.seek(byte_offset)` again before calling `f.write()`.

---

## 6. Student In-Class Checkpoint Questions

1. **Question:** *What happens if you open a file with mode `'w'` and call `seek(0)`?*  
   **Answer:** It does nothing helpful because mode `'w'` already erased the entire file to 0 bytes upon opening. To update existing data, use `'r+'` or `'rb+'`.

2. **Question:** *Why do we subtract 1 in `(record_num - 1) * RECORD_SIZE`?*  
   **Answer:** Because file offsets are 0-indexed. Record 1 begins at byte 0 ($0 \times 32 = 0$).

3. **Question:** *If a text file has varying line lengths, can you still use `seek()`?*  
   **Answer:** You can call `seek()`, but you cannot reliably predict where record $N$ starts without maintaining a separate "index table" or dictionary of byte offsets.

---

## 7. Lab Practice Assignment (Follow-Up)

**Assignment Title:** Direct Access Employee Payroll Lookup
* **Prompt:** Write a program that manages an employee file where each record is 40 bytes:
  * Employee ID (5 chars), Department (10 chars), Hourly Rate (6 chars), Name (18 chars), `\n` (1 char).
* **Requirements:**
  1. Populate the file with at least 5 employees.
  2. Prompt the user for an employee record number (1 through 5).
  3. Jump directly to that employee using `.seek()` and print their information.
  4. Prompt the user to enter a new hourly rate and update that employee's rate in place using mode `'r+'`.
  5. Include `try/except` blocks handling `ValueError` (invalid user input) and `IndexError` (out-of-range record).
