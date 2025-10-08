import logging
import sys
import traceback
from airflow.exceptions import AirflowException
from contextlib import contextmanager
from .ses_utils import send_email_to_support

###
# Returns placeholdered string used in the subject of the email sent
#
# Ex: [Products - Airflow dag quable_to_colombus] - read_configuration
#
# return string
###
def get_error_subject():
    """Renvoie le template de sujet d'email d'erreur.

    Returns:
        str: Modèle ``"{} - {}"`` à formater avec (system_name, function_name).
    """
    return '{} - {}'

def format_exception_info(exc_info, format = None):
    """Formate les informations d'exception.

    Args:
        exc_info (tuple): Tuple retourné par ``sys.exc_info()``.
        format (str | None): ``'html'`` pour HTML, sinon texte brut.

    Returns:
        str: Représentation formatée de l'exception (texte ou HTML).
    """
    exc_type, exc_value, exc_traceback = exc_info

    # Get the full traceback details
    tb_details = traceback.extract_tb(exc_traceback)

    # Get the last frame (where the error occurred)
    last_frame = tb_details[-1]
    filename, line_number, func_name, text = last_frame

    match format:
        case 'html':
            formatted_error = f"""
                <p><b>Error Type:</b> {exc_type.__name__}</p>
                <p><b>Message:</b> {str(exc_value)}</p>
                <p><b>Location:</b>
                    <ul>
                        <li><b>File:</b> {filename}</li>
                        <li><b>Line:</b> {line_number}</li>
                        <li><b>Function:</b> {func_name}</li>
                        <li><b>Code:</b> {text}</li>
                    </ul>
                </p>
            """
        case _:
            formatted_error = f"""
                {'='*50}
                Error Type: {exc_type.__name__}
                Message: {str(exc_value)}
                Location:
                File: {filename}
                Line: {line_number}
                Function: {func_name}
                Code: {text}
                {'='*50}
            """

    return formatted_error

@contextmanager
def error_handling(system_name, function_name):
    """Context manager pour capturer, formater et notifier les erreurs.

    En cas d'exception, un email est envoyé au support et l'erreur est
    relancée sous forme d'``AirflowException`` si le nom du système contient
    ``"airflow"``.

    Args:
        system_name (str): Nom du système/process (ex: ``"products - airflow dag..."``).
        function_name (str): Nom de la fonction/étape exécutée.
    """
    try:
        yield
    except Exception as e:
        error_subject = get_error_subject().format(system_name, function_name)
        formatted_exception = format_exception_info(sys.exc_info())
        formatted_exception_html = format_exception_info(sys.exc_info(), 'html')
        error_message = f"Error while executing {function_name} : \n\n {formatted_exception}"
        error_message_html = f"An error occurred while executing {function_name} : <br><br> {formatted_exception_html}"
        logging.error(error_message)
        send_email_to_support(error_subject, error_message_html)
        
        if 'airflow' in system_name:
            raise AirflowException(error_message)
        else:
            raise e