# viona/__init__.py

# api.py dosyasındaki Viona sınıfını doğrudan paketin dışına açar.
from .api import Viona 

# Telif Hakkı Bilgisi (Kodun en başına eklenmesi talebiniz için bu satırı buraya taşıyorum, 
# böylece her import edildiğinde konsola yazılacaktır.
# Ancak bu tür bilgilerin __init__ yerine README'de olması daha yaygındır.)
# print("2025 - Orvix games Tüm hakları sakıldır") 
# Not: Yayımlanan paketlerde print kullanmak yerine loglama tercih edilir.
# Ben telif hakkını Viona sınıfının __init__ metodunda bıraktım, orası daha uygun.

# Sınıfı direkt olarak viona'dan alınabilmesi için (viona.Viona yerine)
__all__ = ["Viona"]