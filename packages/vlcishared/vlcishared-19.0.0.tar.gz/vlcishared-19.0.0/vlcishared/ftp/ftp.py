from datetime import datetime
import fnmatch
from ftplib import FTP
import logging
import os

import pytz
from vlcishared.utils.interfaces import ConnectionInterface


class FTPClient(ConnectionInterface):
    """Clase que se conecta a un servidor FTP para listar ficheros"""

    def __init__(self, host: str, username: str, password: str, port=21):
        """Inicializa el cliente FTP con los datos de conexión"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ftp = None
        self.log = logging.getLogger(__name__)

    def connect(self) -> None:
        """Intenta conectarse al servidor FTP"""
        try:
            self.log.info(f"Conectado a host: {self.host}")
            self.ftp = FTP()
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
        except Exception as e:
            raise ConnectionRefusedError(f"Conexión fallida: {str(e)}")

    def close(self):
        """Cierra la conexión al servidor FTP"""
        if self.ftp:
            self.ftp.quit()
            self.log.info(f"Conexión a {self.host} cerrada.")

    def list(self, remote_path: str) -> list:
        """Devuelve una lista con los ficheros en el directorio indicado"""
        try:
            self.ftp.cwd(remote_path)
            return self.ftp.nlst()
        except Exception as e:
            raise ConnectionAbortedError(f"Fallo al listar los archivos: {str(e)}")

    def list_matching_files(self, remote_path: str, pattern: str) -> list:
        """Devuelve una lista de ficheros en el directorio indicado que coincidan con el patrón indicado."""
        remote_files = self.list(remote_path)
        matching_files = fnmatch.filter(remote_files, pattern)
        return matching_files

    def download(self, remote_path: str, local_path: str, pattern: str, min_date: datetime = None):
        """
        Descarga uno o varios archivos del servidor FTP al directorio local que cumplan con el patrón especificado
        y cuya fecha de modificación sea mayor a min_date (si se indica).
        - remote_path: ruta en el servidor FTP
        - local_path: directorio en local
        - pattern: patrón estilo shell (ej: '*.csv')
        - min_date: fecha de modificación mínima
        """
        try:
            matching_files = self.list_matching_files(remote_path, pattern)
            if not matching_files:
                raise FileNotFoundError(f"No se encontraron archivos que cumplan el patrón '{pattern}' en {remote_path}")

            for remote_file in matching_files:
                if min_date:
                    resp = self.ftp.sendcmd(f"MDTM {remote_file}")
                    fecha_str = resp.split()[1]
                    fecha_mod = datetime.strptime(fecha_str, "%Y%m%d%H%M%S")  # datetime naive
                    fecha_mod = fecha_mod.replace(tzinfo=pytz.UTC)

                    if fecha_mod <= min_date:
                        self.log.info(f"Saltando {remote_file}, fecha modificación: {fecha_mod} <= {min_date}")
                        continue

                local_file = os.path.join(local_path, os.path.basename(remote_file))
                with open(local_file, "wb") as file:
                    self.ftp.retrbinary(f"RETR {remote_file}", file.write)
                self.log.info(f"Descargado {remote_file} -> {local_file}")
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ConnectionAbortedError(f"Descarga fallida: {str(e)}")

    def delete(self, remote_file_path: str):
        """Elimina un archivo del servidor FTP en la ruta indicada"""
        try:
            self.ftp.delete(remote_file_path)
            self.log.info(f"Archivo eliminado: {remote_file_path}")
        except Exception as e:
            raise ConnectionAbortedError(f"Eliminación fallida: {str(e)}")

    def upload(self, local_file: str, remote_path: str):
        """Sube el fichero indicado desde la máquina local al servidor FTP"""
        try:
            remote_path = os.path.join(remote_path, os.path.basename(local_file))
            with open(local_file, "rb") as file:
                self.ftp.storbinary(f"STOR {remote_path}", file)
        except Exception as e:
            raise ConnectionAbortedError(f"Subida fallida: {str(e)}")

    def execute_with_connection(self, method, *args, **kwargs):
        self.connect()
        try:
            return method(*args, **kwargs)
        finally:
            self.close()
