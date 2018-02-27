# smsfarm
python module which provide interface to smsfarm.sk 

[![Maintainability](https://api.codeclimate.com/v1/badges/32123cb660e485dca9b4/maintainability)](https://codeclimate.com/github/j-mak/smsfarm/maintainability)

## Getting started

### Prerequisites
All dependencies are in `requirements.txt` file and you can install they using following command
```bash
pip install -r requirements.txt
```

### Installing
You can install from source code
```bash
git clone https://github.com/j-mak/smsfarm.git
cd smsfarm
python setup.py develop
```
or you can install this package through pip using following command
```bash
pip install smsfarm
```

### Examples

```python
from smsfarm import Client

client = Client("some-code", "some-id")
client.recipients = '+421900123456'

result = client.send_message("Hello World!")
if result.success:
    # message was sended without any error
    print(result.data) 
    delivery_status = client.get_message_status(result.data)
    if delivery_status.success:
        print(delivery_status.data)
```

## Authors

* **Jozef 'sunny' Mak**

See also the list of [contributors](https://github.com/j-mak/smsfarm/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details