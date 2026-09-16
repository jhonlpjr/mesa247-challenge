from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.exceptions import InvalidStateError, NotFoundError, ValidationError
from app.application.use_cases.call_next import CallNext
from app.application.use_cases.get_queue_entry import GetQueueEntry
from app.application.use_cases.get_restaurant_queue import GetRestaurantQueue
from app.application.use_cases.join_queue import JoinQueue
from app.application.use_cases.get_daily_report import GetDailyReport
from app.application.use_cases.transition_entry import TransitionEntry
from app.domain.enums.queue_status import QueueStatus
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.sqlalchemy_queue_repository import SQLAlchemyQueueRepository
from app.infrastructure.repositories.sqlalchemy_restaurant_repository import SQLAlchemyRestaurantRepository
from app.presentation.schemas.queue_schemas import DailyReportResponse, JoinQueueRequest, QueueEntryResponse, QueueResponse, RestaurantResponse

router = APIRouter()


def repos(db: Session):
    return SQLAlchemyRestaurantRepository(db), SQLAlchemyQueueRepository(db)


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse, tags=["Restaurantes"], summary="Obtener restaurante", description="Devuelve el nombre, país, prefijo telefónico y zona horaria usados por el flujo de la cola.")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = SQLAlchemyRestaurantRepository(db).get(restaurant_id)
    if restaurant is None: raise HTTPException(404, "Restaurant not found")
    return restaurant


@router.post("/restaurants/{restaurant_id}/queue", response_model=QueueEntryResponse, status_code=status.HTTP_201_CREATED, tags=["Cola · Comensal"], summary="Ingresar a la cola", description="Registra un grupo en estado WAITING y devuelve su identificador para seguimiento.")
def join_queue(restaurant_id: int, payload: JoinQueueRequest, db: Session = Depends(get_db)):
    restaurants, queue = repos(db)
    try: return QueueEntryResponse.model_validate(JoinQueue(restaurants, queue).execute(restaurant_id, payload.name, payload.phone, payload.party_size))
    except NotFoundError as exc: raise HTTPException(404, str(exc))
    except ValidationError as exc: raise HTTPException(422, str(exc))


@router.get("/queue/{entry_id}", response_model=QueueEntryResponse, tags=["Cola · Comensal"], summary="Consultar seguimiento", description="Obtiene el estado y la posición actual de un grupo.")
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    try:
        entry, position = GetQueueEntry(SQLAlchemyQueueRepository(db)).execute(entry_id)
        return QueueEntryResponse.model_validate(entry).model_copy(update={"position": position})
    except NotFoundError as exc: raise HTTPException(404, str(exc))


@router.get("/restaurants/{restaurant_id}/queue", response_model=QueueResponse, tags=["Cola · Operación"], summary="Listar cola activa", description="Lista los grupos WAITING y CALLED del día operativo local del restaurante.")
def get_queue(restaurant_id: int, db: Session = Depends(get_db)):
    restaurants, queue = repos(db)
    try: return QueueResponse(entries=[QueueEntryResponse.model_validate(e).model_copy(update={"position": i if e.status == QueueStatus.WAITING else None}) for i, e in enumerate(GetRestaurantQueue(restaurants, queue).execute(restaurant_id), 1)])
    except NotFoundError as exc: raise HTTPException(404, str(exc))


@router.post("/restaurants/{restaurant_id}/queue/call-next", response_model=QueueEntryResponse, tags=["Cola · Operación"], summary="Llamar al siguiente grupo", description="Selecciona atómicamente el grupo WAITING más antiguo y lo pasa a CALLED.")
def call_next(restaurant_id: int, db: Session = Depends(get_db)):
    restaurants, queue = repos(db)
    try:
        entry = CallNext(restaurants, queue).execute(restaurant_id)
        if entry is None: raise HTTPException(404, "No waiting entries")
        return QueueEntryResponse.model_validate(entry)
    except NotFoundError as exc: raise HTTPException(404, str(exc))


@router.post("/queue/{entry_id}/call", response_model=QueueEntryResponse, tags=["Cola · Operación"], summary="Llamar a un grupo", description="Pasa un grupo específico de WAITING a CALLED. La notificación externa se integra fuera de este endpoint.")
def call_entry(entry_id: int, db: Session = Depends(get_db)):
    try:
        result = TransitionEntry(SQLAlchemyQueueRepository(db)).execute(entry_id, QueueStatus.WAITING, QueueStatus.CALLED)
        return QueueEntryResponse.model_validate(result)
    except NotFoundError as exc: raise HTTPException(404, str(exc))
    except (ValueError, InvalidStateError) as exc: raise HTTPException(409, str(exc))


@router.post("/queue/{entry_id}/seat", response_model=QueueEntryResponse, tags=["Cola · Operación"], summary="Marcar grupo como sentado", description="Pasa un grupo previamente llamado de CALLED a SEATED y registra seated_at en UTC.")
def seat_entry(entry_id: int, db: Session = Depends(get_db)):
    try:
        result = TransitionEntry(SQLAlchemyQueueRepository(db)).execute(entry_id, QueueStatus.CALLED, QueueStatus.SEATED)
        return QueueEntryResponse.model_validate(result)
    except NotFoundError as exc: raise HTTPException(404, str(exc))
    except (ValueError, InvalidStateError) as exc: raise HTTPException(409, str(exc))


@router.post("/queue/{entry_id}/cancel", response_model=QueueEntryResponse, tags=["Cola · Operación"], summary="Cancelar grupo", description="Marca como CANCELLED un grupo que aún no fue sentado.")
def cancel_entry(entry_id: int, db: Session = Depends(get_db)):
    queue = SQLAlchemyQueueRepository(db); entry = queue.get(entry_id)
    if entry is None: raise HTTPException(404, "Queue entry not found")
    try: return QueueEntryResponse.model_validate(TransitionEntry(queue).execute(entry_id, entry.status, QueueStatus.CANCELLED))
    except (ValueError, InvalidStateError) as exc: raise HTTPException(409, str(exc))


@router.post("/queue/{entry_id}/no-show", response_model=QueueEntryResponse, tags=["Cola · Operación"], summary="Marcar inasistencia", description="Pasa un grupo CALLED a NO_SHOW cuando no se presenta.")
def no_show_entry(entry_id: int, db: Session = Depends(get_db)):
    try:
        result = TransitionEntry(SQLAlchemyQueueRepository(db)).execute(entry_id, QueueStatus.CALLED, QueueStatus.NO_SHOW)
        return QueueEntryResponse.model_validate(result)
    except NotFoundError as exc: raise HTTPException(404, str(exc))
    except (ValueError, InvalidStateError) as exc: raise HTTPException(409, str(exc))


@router.get("/restaurants/{restaurant_id}/reports/daily", response_model=DailyReportResponse, tags=["Reportes"], summary="Obtener reporte diario", description="Calcula ingresos, atenciones, cancelaciones e inasistencias para un día calendario en la zona horaria del restaurante.")
def daily_report(restaurant_id: int, date: date = Query(..., description="Día local a consultar en formato YYYY-MM-DD.", examples=["2026-09-15"]), db: Session = Depends(get_db)):
    restaurants, queue = repos(db)
    try: return GetDailyReport(restaurants, queue).execute(restaurant_id, date)
    except NotFoundError as exc: raise HTTPException(404, str(exc))
