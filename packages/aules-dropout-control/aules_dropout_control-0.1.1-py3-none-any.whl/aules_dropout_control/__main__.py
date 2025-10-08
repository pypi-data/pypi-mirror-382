
import argparse
from aules_dropout_control.webscraper import WebScraper
from typing import List, Dict, Any

import logging
import os

# Configure logging level from LOG_LEVEL env variable, default to ERROR
log_level_str = os.environ.get("LOG_LEVEL", "ERROR").upper()
log_level = getattr(logging, log_level_str, logging.ERROR)
logging.basicConfig(level=log_level)

def get_participant_info(scraper: WebScraper, course_id: int, course_name: str, username: str, password: str) -> List[Dict[str, Any]]:
    # Get CSV string from webscraper
    csv_str = scraper.get_participants_info(course_id, username, password)
    import csv
    import io
    reader = csv.DictReader(io.StringIO(csv_str))
    return list(reader)

def main():
    import configparser
    parser = argparse.ArgumentParser(
        description=(
            "Obtiene los usuarios que no se han conectado en un número de días a uno o varios cursos de Aules.\n"
            "Requiere un archivo de credenciales en formato INI."
            "Formato del archivo de credenciales (INI):\n\n"
            "[credentials]\n"
            "username = tu_usuario\n"
            "password = tu_contraseña\n\n"
            "Por seguridad, protege el archivo de credenciales y no lo subas a repositorios públicos.\n\n"
            "Ejemplo de uso:\n\n"
            "aules-dropout-control <course_id> --credentials example_credentials.ini [--days-without-connection N]\n\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "course",
        help="ID del curso (se puede ver en la URL de Aules) o ruta a un archivo con varios IDs de curso (uno por línea, opcionalmente con nombre separado por coma. Por ejemplo: 123,Curso de Matemáticas)"
    )
    parser.add_argument(
        "--days-without-connection",
        type=int,
        default=10,
        help="Sólo mostrará a los usuarios que no se han conectado en ese número de días (por defecto: 10)"
    )
    parser.add_argument(
        "--credentials",
        required=True,
        help=(
            "Ruta al archivo de credenciales INI. "
            "Debe contener la sección [credentials] con username y password. "
        )
    )
    import os
    args = parser.parse_args()

    config = configparser.ConfigParser()
    try:
        config.read(args.credentials)
        username = config.get('credentials', 'username')
        password = config.get('credentials', 'password')
    except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError) as e:
        print(f"\n[ERROR] Archivo de credenciales inválido: {e}\n")
        print("El archivo debe tener el siguiente formato:\n")
        print("[credentials]\nusername = tu_usuario\npassword = tu_contraseña\n")
        exit(1)

    from typing import List, Tuple, Dict, Any
    courses: List[Tuple[str, str]] = []
    use_file = os.path.isfile(args.course)
    if use_file:
        with open(args.course, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',', 1)
                course_id_part = parts[0].strip()
                course_name_part = parts[1].strip() if len(parts) > 1 else ""
                if course_id_part:
                    courses.append((course_id_part, course_name_part))
    else:
        courses = [(args.course, "")]

    # Create a single WebScraper instance and login once
    logging.info(f"Checking users not connected in last {args.days_without_connection} days")
    scraper = WebScraper(username, password, days_without_connection=args.days_without_connection)
    scraper.login()

    all_participants: List[Dict[str, Any]] = []
    for cid, cname in courses:
        try:
            participants = get_participant_info(scraper, int(cid), cname, username, password)
            if use_file:
                for p in participants:
                    p['course_id'] = cid
                    p['course_name'] = cname
                    all_participants.append(p)
            else:
                all_participants.extend(participants)
        except Exception as e:
            print(f"Error processing course ID {cid}: {e}")

    # Output single CSV for all participants
    if all_participants:
        import csv
        import sys
        if use_file:
            fieldnames = ['course_id', 'course_name', 'name', 'user_name', 'email', 'roles', 'acceso']
        else:
            fieldnames = ['name', 'user_name', 'email', 'roles', 'acceso']
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_participants:
            writer.writerow({k: p.get(k, '') for k in fieldnames})

if __name__ == "__main__":
    main()
