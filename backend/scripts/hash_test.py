import bcrypt
from passlib.context import CryptContext

print('bcrypt module', bcrypt)
print('has __about__', hasattr(bcrypt, '__about__'))
print('bcrypt.__version__', getattr(bcrypt, '__version__', None))
try:
    print('bcrypt.hashpw test')
    print(bcrypt.hashpw(b'short', bcrypt.gensalt()))
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
    print('passlib hash test')
    print(ctx.hash('short'))
except Exception as e:
    import traceback
    traceback.print_exc()
