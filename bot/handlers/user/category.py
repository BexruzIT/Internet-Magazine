import logging
import uuid
from typing import List

from aiogram import Router, F, html, Bot
from aiogram.filters import Command
from aiogram.types.labeled_price import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (Message, CallbackQuery, InlineQueryResultArticle, InputTextMessageContent,
                           InlineQuery, PreCheckoutQuery, SuccessfulPayment)

from bot.app import PROVIDER_TOKEN
from bot.handlers.api.response import api_response
from bot.keyboards.call_data.callbacks import (CategoryCallback, SubcategoryCallback, ProductCallback)
from bot.utils.helper.help_time import time_formatter, format_price
from bot.keyboards.call_data.callbacks import BuyCallback
from bot.keyboards.inline.button import (cateogry_builder, subcategories_builder, products_builder,
                                         product_detail_builder, quantity_selector_builder)

category_router = Router()


@category_router.message(Command('category'))
async def show_categories(message: Message):
    categories = api_response.get_categories()
    category_keyboard_datas = [(j['id'], j['name']) for j in categories]

    await message.answer(
        text="<b>🏠 Основные категории:</b>",
        reply_markup=cateogry_builder(category_keyboard_datas, 2),
        parse_mode="HTML"
    )


@category_router.callback_query(CategoryCallback.filter())
async def category_handler(call: CallbackQuery, callback_data: CategoryCallback):
    if callback_data.action == 'view':
        category = api_response.get_categories(callback_data.category_id)
        subcategory_keyboard_datas = [(sub['id'], sub['category'], sub['name']) for sub in category['subcategories']]

        await call.message.edit_text(
            text=f"{html.bold(category['name'])} kategoriyasi:",
            reply_markup=subcategories_builder(subcategory_keyboard_datas, 2)
        )

    elif callback_data.action == 'back':
        categories = api_response.get_categories()
        category_keyboard_datas = [(cat['id'], cat['name']) for cat in categories]

        await call.message.edit_text(
            text="<b>🏠 Основные категории:</b>",
            reply_markup=cateogry_builder(category_keyboard_datas, 2),
            parse_mode="HTML"
        )

    await call.answer()


@category_router.callback_query(SubcategoryCallback.filter())
async def show_subcategories(call: CallbackQuery, callback_data: SubcategoryCallback):
    category_id = callback_data.category_id
    subcategory_id = callback_data.subcategory_id

    if callback_data.action == 'view':
        subcategory = api_response.get_subcateogries(subcategory_id)
        products_keyboard_datas = [(p['id'], p['subcategory'], p['name']) for p in subcategory['products']]

        await call.message.edit_text(
            text=f"{html.bold(subcategory['name'])}:",
            reply_markup=products_builder(products_keyboard_datas, 2, cat_id=category_id))

    elif callback_data.action == 'back':
        categories = api_response.get_categories(callback_data.category_id)
        subcategory_keyboard_datas = [(s['id'], s['category'], s['name']) for s in categories['subcategories']]

        await call.message.edit_text(
            text=f"{html.bold(categories['name'])}:",
            reply_markup=subcategories_builder(subcategory_keyboard_datas, 2))

    await call.answer()


@category_router.callback_query(ProductCallback.filter(F.action == 'paginate'))
async def paginate_products(call: CallbackQuery, callback_data: ProductCallback):
    subcategory = api_response.get_subcateogries(callback_data.subcategory_id)
    products_keyboard_datas = [(p['id'], p['subcategory'], p['name']) for p in subcategory['products']]

    await call.message.edit_text(
        text=f"{html.bold(subcategory['name'])}:",
        reply_markup=products_builder(
            products_keyboard_datas,
            cols=2,
            cat_id=subcategory['category'],
            page=callback_data.page
        )
    )

    await call.answer()


@category_router.callback_query(ProductCallback.filter())
async def show_products(call: CallbackQuery, callback_data: ProductCallback):
    subcategory_id = callback_data.subcategory_id
    product_id = callback_data.product_id

    if callback_data.action == 'view':
        product = api_response.get_product(product_id)
        product_name = f"🛍 Продукт: {product['name']}"
        product_desc = f"📝 Описание:: {product['description'][:300]}..."
        product_price = f"💳 Цена: {float(product['price']):,.0f} сум"
        product_stock = product['stock']
        product_stock = f"📦 Есть {product_stock} штук {product['name']}." if product_stock else '❌ Пока не доступен!'
        mark = '💾' if time_formatter(product['created_at']) == time_formatter(product['updated_at']) else '🔄'
        product_time = f"{mark} ⏳ {time_formatter(product['updated_at'])}"
        product_image = product['image']

        product_detail = (f"{html.bold(product_name)}\n\n"
                          f"{html.italic(product_desc)}\n\n"
                          f"{html.bold(product_price)}\n"
                          f"{html.bold(product_stock)}\n\n"
                          f"{html.bold(product_time)}")
        await call.message.edit_text(
            text=product_detail,
            reply_markup=product_detail_builder(subcategory_id, product_id, page=callback_data.page))

    elif callback_data.action == 'back':
        subcategory = api_response.get_subcateogries(subcategory_id)
        category_id = subcategory['category']
        products = [(p['id'], p['subcategory'], p['name']) for p in subcategory['products']]

        await call.message.edit_text(
            text=f"{html.bold(subcategory['name'])}:",
            reply_markup=products_builder(products, 2, cat_id=category_id))

    await call.answer()


@category_router.callback_query(BuyCallback.filter(F.action == "buy"))
async def buy_product_handler(call: CallbackQuery, callback_data: BuyCallback):
    product = api_response.get_product(callback_data.product_id)
    omborda = product['stock'] - callback_data.quantity
    text = (
        f"🛍 Продукт: {product['name']}\n"
        f"💰 Цена: {float(product['price']):,.0f} сум\n"
        f"🏪 На складе: {f'{omborda} осталось' if omborda else 'Не осталось'}\n"
        f"📦 Количество: {callback_data.quantity} ta\n"
        f"💳 Всего: {float(product['price']) * callback_data.quantity:,.0f} сум\n\n"
        f"Выберите количество:"
    )
    if product['stock'] < callback_data.quantity:
        return await call.answer('⚠️ Количество товаров ограничено!', show_alert=True)

    await call.message.edit_text(
        text=text,
        reply_markup=quantity_selector_builder(callback_data.product_id, callback_data.quantity, callback_data.page)
    )

    await call.answer()


# @category_router.callback_query(BuyCallback.filter(F.action == "confirm"))
# async def confirm_purchase_handler(call: CallbackQuery, callback_data: BuyCallback):
#     product = api_response.get_product(callback_data.product_id)
#     total_price = float(product['price']) * callback_data.quantity
#
#     # Bu yerda haqiqiy sotib olish logikasi bo'lishi kerak
#     # Misol uchun, APIga so'rov yuborish yoki ma'lumotlar bazasiga yozish
#
#     await call.message.edit_text(
#         text=(
#             f"✅ Sotib olish muvaffaqiyatli yakunlandi!\n\n"
#             f"🛍 Mahsulot: {product['name']}\n"
#             f"📦 Miqdori: {callback_data.quantity} ta\n"
#             f"💳 Jami: {total_price:,.0f} so'm\n\n"
#             f"Tez orada operatorlarimiz siz bilan bog'lanishadi."
#         ),
#         reply_markup=InlineKeyboardBuilder().button(
#             text="🏠 Bosh menyu",
#             callback_data=CategoryCallback(action="back")
#         ).as_markup()
#     )
#     await call.answer()

@category_router.callback_query(BuyCallback.filter(F.action == "confirm"))
async def confirm_purchase_handler(call: CallbackQuery, callback_data: BuyCallback, bot: Bot):
    product = api_response.get_product(callback_data.product_id)
    total_price = int(float(product['price']) * callback_data.quantity * 100)  # Telegram uchun cents formatida

    # Invoice yuborish
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f"{product['name']} (x{callback_data.quantity})",
        description=f"{product['description'][:100]}...",
        payload=f"order_{product['id']}_{callback_data.quantity}",
        provider_token=PROVIDER_TOKEN,  # BotFather dan olingan token
        currency="UZS",  # Yoki "USD" boshqa valyuta
        prices=[
            LabeledPrice(
                label=f"{product['name']} (x{callback_data.quantity})",
                amount=total_price
            )
        ],
        photo_url=product['image'],  # https://images.uzum.uz/crskc8ji153t30undvm0/original.jpg',  # Agar rasm bo'lsa
        photo_width=512,
        photo_height=512,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,  # Agar yetkazib berish kerak bo'lsa True qiling
        is_flexible=False,
    )
    await call.answer()


@category_router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id,
        ok=True,
        error_message="Произошла ошибка при платеже. Попробуйте еще раз позже."
    )


@category_router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment_info = message.successful_payment
    product_id = int(payment_info.invoice_payload.split('_')[1])
    quantity = int(payment_info.invoice_payload.split('_')[2])

    # Buyurtmani ma'lumotlar bazasiga yozish
    order_data = {
        "user_id": message.from_user.id,
        "product_id": product_id,
        "quantity": quantity,
        "total_amount": payment_info.total_amount / 100,  # cents dan asosiy birlikka
        "phone_number": payment_info.order_info.phone_number,
        "email": payment_info.order_info.email,
        "full_name": payment_info.order_info.name,
    }

    # APIga buyurtma yuborish
    api_response.create_order(order_data)

    await message.answer(
        text=(
            f"✅ Оплата прошла успешно!\n\n"
            f"💳 Сумма платежа: {payment_info.total_amount / 100:,.0f} so'm\n"
            f"📦 Номер заказа: {payment_info.invoice_payload}\n\n"
            f"Наши операторы свяжутся с вами в ближайшее время."
        ),
        reply_markup=InlineKeyboardBuilder().button(
            text="🏠 Главное меню",
            callback_data=CategoryCallback(action="back")
        ).as_markup()
    )


@category_router.callback_query(BuyCallback.filter(F.action == "cancel"))
async def cancel_purchase_handler(call: CallbackQuery, callback_data: BuyCallback):
    product = api_response.get_product(callback_data.product_id)

    await call.message.edit_text(
        text=f"Покупка отменена: {product['name']}",
        reply_markup=product_detail_builder(
            sub_id=product['subcategory'],
            product_id=callback_data.product_id,
            page=callback_data.page
        )
    )
    await call.answer()


@category_router.inline_query()
async def inline_query_handler(inline: InlineQuery):
    query: str = inline.query.strip()

    # Bo‘sh so‘rovga default javob berish (ixtiyoriy)
    if not query:
        await inline.answer(
            results=[
                InlineQueryResultArticle(
                    id="default",
                    title="Введите название продуктаЖ",
                    input_message_content=InputTextMessageContent(
                        message_text="Напишите, пожалуйста, название продукта."
                    )
                )
            ],
            cache_time=1
        )
        return

    try:
        products: List[dict] = api_response.search_products(find=query) or []
    except Exception as e:
        logging.exception("API dan ma’lumot olishda xatolik:")
        await inline.answer(
            results=[
                InlineQueryResultArticle(
                    id="error",
                    title="Xatolik yuz berdi",
                    description="Mahsulotlarni olishda muammo yuz berdi.",
                    input_message_content=InputTextMessageContent(
                        message_text="Kechirasiz, ma’lumotlarni olishda xatolik yuz berdi. Keyinroq urinib ko‘ring."
                    )
                )
            ],
            cache_time=1
        )
        return

    results: List[InlineQueryResultArticle] = []

    for product in products:
        name = product.get("name", "Noma’lum")
        description = product.get("description", "Tavsifi mavjud emas")
        price = product.get("price")

        formatted_price = format_price(price) if price else "Noma’lum"

        product_name = f"🛍 Mahsulot: {product.get('name', 'Noma’lum')}"
        product_desc = f"📝 Batavsil: {product.get('description', 'Tavsifi mavjud emas')[:300]}..."
        product_price = f"💳 Narxi: {formatted_price} so'm"
        product_stock = product.get('stock', 'Noma`lum')
        product_stock = f"📦 {product_stock} ta {product['name']} bor." if product_stock else '❌ Hozircha mavjud emas!'
        mark = '💾' if time_formatter(product['created_at']) == time_formatter(product['updated_at']) else '🔄'
        product_time = f"{mark} ⏳ {time_formatter(product['updated_at'])}"
        product_image = product['image']

        product_detail = (f"{html.bold(product_name)}\n\n"
                          f"{html.italic(product_desc)}\n\n"
                          f"{html.bold(product_price)}\n"
                          f"{html.bold(product_stock)}\n\n"
                          f"{html.bold(product_time)}")

        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{name}",
                description=f"{formatted_price} so'm\n{description}",
                thumbnail_url=f'https://storage.kun.uz/source/10/z8qGXj646Qve_FIaYGQPpAVPTj9Pg5Dl.jpg',
                input_message_content=InputTextMessageContent(
                    message_text=product_detail
                ),

            )
        )

    if not results:
        results.append(
            InlineQueryResultArticle(
                id="not_found",
                title="Ничего не найдено",
                description=f"“{query}” товаров не найдено.",
                input_message_content=InputTextMessageContent(
                    message_text=f"“{query}” товаров не найдено."
                )
            )
        )

    await inline.answer(results=results, cache_time=1)


@category_router.message()
async def clear_manual_message(message: Message):
    logging.info(message.model_json_schema())
    if message.text and not message.text.startswith("[inline]"):
        try:
            await message.delete()
        except Exception as e:
            logging.warning(f"Ошибка удаления сообщения: {e}")