from django.db import models

class UserRole(models.TextChoices):
    FARMER = "farmer", "Farmer"
    CUSTOMER = "customer", "Customer"
    EQUIPMENT_OWNER = "equipment_owner", "Equipment Owner" #equipment owner
    STAFF = "staff", "Staff"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class PaymentMethod(models.TextChoices):
    WALLET = "wallet", "Wallet"
    MPESA = "mpesa", "M-Pesa"
    CARD = "card", "Card"
    PAY_ON_DELIVERY = "pay_on_delivery", "Pay on Delivery"
    

class Country(models.TextChoices):
    KENYA = "KE", "Kenya"
    ALGERIA = "DZ", "Algeria"
    ANGOLA = "AO", "Angola"
    BENIN = "BJ", "Benin"
    BOTSWANA = "BW", "Botswana"
    BURKINA_FASO = "BF", "Burkina Faso"
    BURUNDI = "BI", "Burundi"
    CABO_VERDE = "CV", "Cabo Verde"
    CAMEROON = "CM", "Cameroon"
    CHAD = "TD", "Chad"
    COMOROS = "KM", "Comoros"
    COTE_DIVOIRE = "CI", "Côte d'Ivoire"
    DJIBOUTI = "DJ", "Djibouti"
    EGYPT = "EG", "Egypt"
    EQUATORIAL_GUINEA = "GQ", "Equatorial Guinea"
    ERITREA = "ER", "Eritrea"
    ETHIOPIA = "ET", "Ethiopia"
    GABON = "GA", "Gabon"
    GAMBIA = "GM", "Gambia"
    GHANA = "GH", "Ghana"
    GUINEA = "GN", "Guinea"
    LESOTHO = "LS", "Lesotho"
    LIBERIA = "LR", "Liberia"
    LIBYA = "LY", "Libya"
    MADAGASCAR = "MG", "Madagascar"
    MALAWI = "MW", "Malawi"
    MALI = "ML", "Mali"
    MAURITANIA = "MR", "Mauritania"
    MAURITIUS = "MU", "Mauritius"
    MOROCCO = "MA", "Morocco"
    MOZAMBIQUE = "MZ", "Mozambique"
    NAMIBIA = "NA", "Namibia"
    NIGER = "NE", "Niger"
    NIGERIA = "NG", "Nigeria"
    RWANDA = "RW", "Rwanda"
    SENEGAL = "SN", "Senegal"
    SEYCHELLES = "SC", "Seychelles"
    SIERRA_LEONE = "SL", "Sierra Leone"
    SOMALIA = "SO", "Somalia"
    SOUTH_AFRICA = "ZA", "South Africa"
    SOUTH_SUDAN = "SS", "South Sudan"
    SUDAN = "SD", "Sudan"
    TANZANIA = "TZ", "Tanzania"
    TOGO = "TG", "Togo"
    TUNISIA = "TN", "Tunisia"
    UGANDA = "UG", "Uganda"
    ZAMBIA = "ZM", "Zambia"
    ZIMBABWE = "ZW", "Zimbabwe"


COUNTRY_NUMERIC = {
    "KE": "254",
}
APP_CODE = "01"
PRODUCT_CODE = "01"  # wallet
