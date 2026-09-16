from datetime import datetime, timezone

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.restaurant_model import RestaurantModel


def main():
    with SessionLocal() as db:
        restaurants = [
            (1, "La Terraza Azul", "PE", "+51", "America/Lima"),
            (2, "Cuatro Vientos", "PE", "+51", "America/Lima"),
            (3, "Casa Mediterránea", "CL", "+56", "America/Santiago"),
        ]
        for id_, name, country, phone_code, zone in restaurants:
            item = db.get(RestaurantModel, id_)
            if item is None:
                db.add(RestaurantModel(id=id_, name=name, country_code=country, phone_country_code=phone_code, timezone=zone, created_at=datetime.now(timezone.utc)))
                print(f"Created restaurant {id_}: {name}")
            else:
                changed = item.name != name or item.country_code != country or item.phone_country_code != phone_code or item.timezone != zone
                item.name, item.country_code, item.phone_country_code, item.timezone = name, country, phone_code, zone
                if changed: print(f"Updated restaurant {id_}: {name}")
        db.commit()


if __name__ == "__main__": main()
