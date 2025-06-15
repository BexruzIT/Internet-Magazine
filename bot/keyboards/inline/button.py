from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.call_data.callbacks import (CategoryCallback,
                                               SubcategoryCallback,
                                               ProductCallback)
from bot.keyboards.call_data.callbacks import BuyCallback


def cateogry_builder(datas, cols):
    builder = InlineKeyboardBuilder()
    for id, text in datas:
        builder.button(text=text, callback_data=CategoryCallback(action='view', category_id=id))
    builder.adjust(cols)
    return builder.as_markup()


def subcategories_builder(datas, cols):
    builder = InlineKeyboardBuilder()
    for sub_id, cat_id, text in datas:
        builder.button(text=text,
                       callback_data=SubcategoryCallback(action='view',
                                                         category_id=cat_id,
                                                         subcategory_id=sub_id))
    builder.button(
        text="↩️ Назад",
        callback_data=CategoryCallback(action="back")
    )
    builder.adjust(cols)
    return builder.as_markup()


def products_builder(datas, cols, cat_id, page: int = 0):
    builder = InlineKeyboardBuilder()
    start_ofset = page * 5
    end_ofset = start_ofset + 5

    for prod_id, sub_id, text in datas[start_ofset: end_ofset]:
        builder.button(text=text,
                       callback_data=ProductCallback(action='view',
                                                     subcategory_id=sub_id,
                                                     product_id=prod_id,
                                                     page=page))
    builder.button(
        text="↩️ Назад",
        callback_data=SubcategoryCallback(action='back', category_id=cat_id)
    )

    if page > 0:
        builder.button(
            text='⬅️ Предыдущий', callback_data=ProductCallback(
                action='paginate',
                subcategory_id=datas[0][1],
                prod_id=None,
                page=page - 1)
        )

    if end_ofset < len(datas):
        builder.button(
            text='➡️ Следующий', callback_data=ProductCallback(
                action='paginate',
                subcategory_id=datas[0][1],
                prod_id=None,
                page=page + 1)
        )

    builder.adjust(cols)
    return builder.as_markup()


def product_detail_builder(sub_id, product_id, page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.button(text='🛒 Купить', callback_data=BuyCallback(action="buy", product_id=product_id, page=page))
    builder.button(
        text="↩️ Назад",
        callback_data=ProductCallback(action='back', subcategory_id=sub_id)
    )
    if page:
        builder.button(
            text="⬇️ Выйти",
            callback_data=ProductCallback(action='paginate', subcategory_id=sub_id, page=page)
        )
    builder.adjust(2)
    return builder.as_markup()


def buy_product_builder(product_id, quantity=1, page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Подтвердить",
        callback_data=BuyCallback(action="confirm", product_id=product_id, quantity=quantity, page=page)
    )
    builder.button(
        text="❌ Отменить",
        callback_data=BuyCallback(action="cancel", product_id=product_id, page=page)
    )
    builder.adjust(2)
    return builder.as_markup()


def quantity_selector_builder(product_id, current_quantity, page=0):
    builder = InlineKeyboardBuilder()

    # Kamaytirish tugmasi
    if current_quantity > 1:
        builder.button(
            text="➖",
            callback_data=BuyCallback(action="buy", product_id=product_id, quantity=current_quantity - 1, page=page)
        )

    # Miqdor ko'rsatkichi
    builder.button(
        text=f"{current_quantity}",
        callback_data=BuyCallback(action="buy", product_id=product_id, quantity=current_quantity, page=page)
    )

    # Oshirish tugmasi
    builder.button(
        text="➕",
        callback_data=BuyCallback(action="buy", product_id=product_id, quantity=current_quantity + 1, page=page)
    )

    # Tasdiqlash va bekor qilish
    builder.button(
        text="✅ Подтвердить",
        callback_data=BuyCallback(action="confirm", product_id=product_id, quantity=current_quantity, page=page)
    )
    builder.button(
        text="❌ Отменить",
        callback_data=BuyCallback(action="cancel", product_id=product_id, page=page)
    )

    builder.adjust(3, 2)
    return builder.as_markup()