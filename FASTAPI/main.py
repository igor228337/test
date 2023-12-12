from fastapi import FastAPI
from FASTAPI.roters.auth import (user, async_db_session, base, logger, TransactionModel, Depends, UserModel,
                                 get_current_active_user, HTTPException, status, Transaction)

app = FastAPI()


@user.post("/transaction", status_code=201)
async def get_data(request: TransactionModel = Depends(TransactionModel),
                   current_user: UserModel = Depends(get_current_active_user)):
    if request.login.find(": ") >= 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=request.login.split(": ")[-1])
    elif type(request.many) is not float:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=request.many)

    logger.info(f"Создан запрос на транзакцию для пользователя: {current_user.login}")
    await Transaction.create(Transaction(login=request.login, many=request.many, status=False))
    return {"Всё": "ЗБС"}


@user.post("/pay")
async def pay_qiwi(current_user: UserModel = Depends(get_current_active_user)):
    pass


app.include_router(user)
app.include_router(base)





logger.info("Все роутера подключены")
