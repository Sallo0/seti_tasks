# port scanner
Сканер TCP и UDP портов.

Достоинства: 
- Работает
- Параллельная реализация

Для запуска нужно ввести доменное имя или ip и указать диапазон сканируемых портов
```sh
python port_scanner.py google.com 0 5000
```
Пример вывода
```sh
python port_scanner.py google.com 0 5000

173.194.222.100:   80 is open
173.194.222.100:  443 is open
```
