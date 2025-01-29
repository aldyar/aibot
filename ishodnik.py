@user.callback_query(F.data.startswith('o_'))
async def check_order(query: CallbackQuery):
    invoice_id = query.data.split("_")[1]
    invoice = await get_invoice(invoice_id)

    if 'result' not in invoice:
        await query.answer("Ошибка: не удалось получить данные по счету.")
        await query.message.answer("Не удалось получить информацию о платеже.")
        return

    status = invoice["result"]["status"]

    if status in {"paid", "paid_over"}:
        # Проверяем, обработан ли уже этот платеж
        if await is_payment_processed(invoice_id):
            await query.answer("Этот платёж уже обработан!")
            await query.message.answer("❗ Этот платёж уже зачислен на ваш баланс.")
            return

        # Начисляем баланс
        user_id = query.from_user.id
        amount = float(invoice["result"]["amount"])
        await add_balance(user_id, amount)

        # Фиксируем, что платёж обработан
        await mark_payment_as_processed(invoice_id, user_id, amount)

        await query.answer()
        await query.message.answer(f"✅ Счет оплачен! Ваш баланс пополнен на {amount}₽")
    else:
        await query.message.answer('❌ Счет не оплачен!')


async def add_balance(user_id: int, amount: float):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def mark_payment_as_processed(invoice_id: str, user_id: int, amount: float):
    """Помечаем платёж как обработанный"""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO payments (invoice_id, user_id, amount, is_processed) VALUES (?, ?, ?, 1)",
            (invoice_id, user_id, amount)
        )
        await db.commit()


async def is_payment_processed(invoice_id: str) -> bool:
    """Проверяем, был ли уже обработан этот платёж"""
    async with get_db() as db:
        result = await db.execute(
            "SELECT 1 FROM payments WHERE invoice_id = ? AND is_processed = 1",
            (invoice_id,)
        )
        return (await result.fetchone()) is not None
