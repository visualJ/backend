# Backend

Das Backend der Routen Webapp ist in Python geschrieben und nutzt Django.
Das Backend bietet eine HTTP-Schnittstelle (nicht ganz RESTful, aber close enough) an, die vom Angularclient oder anderen Clients (Apps etc.) angesprochen werden kann. Im [Wiki](https://github.com/visualJ/backend/wiki) gibt es alle Infos zur API.

## Lokal ausführen

Folgendes ist zu tun, um das backend lokal auszuführen:
```bash
git clone https://github.com/visualJ/backend.git
cd backend
pip install -r requirements.txt
./manage.py migrate
./manage.py runserver
```

Die letzt Zeile startet den Server. Unter http://localhost:8000/ kann die API dann aufgerufen werden, z.B: http://localhost:8000/api/test.

## Deployen

Um Änderungen zu deployen, müssen diese zunächst comittet werden. Dann kann `eb deploy` aufgerufen werden.

Hat man das noch nie gemacht, sind das erste mal ein paar Schritte nötig:
- aws cli und eb cli installieren
  - `pip install awscli`
  - `pip install awsebcli --upgrade --user`
- aws credentials konfigurieren: key id, secret key und default region setzen
  - `aws configure`
  - default region muss entsprechend der Einstellung in der AWS Console gesetzt werden (nachschauen, wo das backend liegt)
- eb projekt initialisieren
  - `eb init backend`
  
Dann sollte das Deployen auch gehen.
