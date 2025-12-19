PAGE_SIZE = 4096
HEADER_SIZE = 16
SLOT_SIZE = 4
PAGE_ID_OFFSET = 0
SLOT_COUNT_OFFSET = 4
FREE_START_OFFSET = 6
FREE_END_OFFSET = 8


def get_slot_count(page: bytearray) -> int:
    return int.from_bytes(page[SLOT_COUNT_OFFSET:SLOT_COUNT_OFFSET+2], "little")


def set_slot_count(page: bytearray, count) -> bytearray:
    print("new count = ", count)
    page[SLOT_COUNT_OFFSET:SLOT_COUNT_OFFSET+2] = count.to_bytes(2, "little")
    return page


def get_free_start(page: bytearray) -> int:
    return int.from_bytes(page[FREE_START_OFFSET:FREE_START_OFFSET+2], "little")


def set_free_start(page: bytearray, value: int) -> bytearray:
    page[FREE_START_OFFSET:FREE_START_OFFSET+2] = value.to_bytes(2, "little")
    return page


def get_free_end(page: bytearray) -> int:
    return int.from_bytes(page[FREE_END_OFFSET:FREE_END_OFFSET+2], "little")


def set_free_end(page: bytearray, value: int) -> bytearray:
    page[FREE_END_OFFSET:FREE_END_OFFSET+2] = value.to_bytes(2, "little")
    return page


def add_slot(page, row_offset: int, row_length: int) -> tuple[int, bytearray]:
    slot_count = get_slot_count(page)
    free_start = get_free_start(page)
    # Position where this slot entry will be written
    slot_pos = free_start
    # Write slot entry (offset + length)
    page[slot_pos:slot_pos+2] = row_offset.to_bytes(2, "little")
    page[slot_pos+2:slot_pos+4] = row_length.to_bytes(2, "little")
    # Update header
    modified_page1 = set_slot_count(page, slot_count + 1)
    modified_page2 = set_free_start(modified_page1, free_start + SLOT_SIZE)
    return slot_count, modified_page2


def insert_row(page: bytearray, row_bytes: bytes) -> tuple[int, bytearray]:
    free_end = get_free_end(page)
    row_length = len(row_bytes)
    new_row_offset = free_end - row_length
    free_start = get_free_start(page)
    if new_row_offset <= free_start + 4:
        return -1, bytearray(0)
    # condition has to be added to ensure the page is not overfilled
    page[new_row_offset: free_end] = row_bytes
    modified_page1 = set_free_end(page, new_row_offset)
    slot_id, modified_page2 = add_slot(modified_page1, new_row_offset, row_length)
    return slot_id, modified_page2


def read_row(page: bytearray, slot_count: int) -> str:
    # since a slot row is represented by 4 bytes (2 for row offset and 2 for row length), we will count by 4s
    slot_row_position = (SLOT_SIZE * slot_count) + HEADER_SIZE
    row_offset = int.from_bytes(page[slot_row_position: slot_row_position+2], "little")
    row_length = int.from_bytes(page[slot_row_position+2: slot_row_position+4], "little")
    row_bytes = page[row_offset: row_offset+row_length]
    return row_bytes.decode("utf-8")


def create_page(page_id: int) -> bytearray:
    page = bytearray(PAGE_SIZE)
    page[PAGE_ID_OFFSET:PAGE_ID_OFFSET+2] = page_id.to_bytes(2, "little")
    page[SLOT_COUNT_OFFSET:SLOT_COUNT_OFFSET+2] = (0).to_bytes(2, "little")
    page[FREE_START_OFFSET: FREE_START_OFFSET+2] = HEADER_SIZE.to_bytes(2, "little")
    page[FREE_END_OFFSET:FREE_END_OFFSET+2] = PAGE_SIZE.to_bytes(2, "little")
    return page
