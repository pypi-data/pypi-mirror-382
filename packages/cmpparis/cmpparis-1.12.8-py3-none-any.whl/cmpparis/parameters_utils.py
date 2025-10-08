import boto3

aws_region_name = 'eu-west-3'

def get_region_name():
    """Renvoie la région AWS utilisée par défaut.

    Returns:
        str: Code de région (ex: ``eu-west-3``).
    """
    return aws_region_name

### SSM Parameter Store ###

def get_parameter(system, param_name = None):
    """Récupère un paramètre unique dans AWS Systems Manager Parameter Store.

    Si le nom du paramètre contient ``password`` ou ``secret``, la récupération
    utilise ``WithDecryption=True``.

    Args:
        system (str): Préfixe du chemin (ex: ``"mit"``) utilisé dans SSM.
        param_name (str | None): Nom du paramètre ou ``None`` pour lire ``/{system}``.

    Returns:
        str | None: Valeur du paramètre si trouvée, sinon ``None``.
    """
    try:
        ssm = boto3.client('ssm', region_name=aws_region_name)

        if param_name is not None:
            if 'password' in param_name or 'secret' in param_name:
                parameter = ssm.get_parameter(Name=f'/{system}/{param_name}', WithDecryption=True)
                param_value = parameter['Parameter']['Value']
            else:
                parameter = ssm.get_parameter(Name=f'/{system}/{param_name}')
                param_value = parameter['Parameter']['Value']
        else:
            parameter = ssm.get_parameter(Name=f'/{system}')
            param_value = parameter['Parameter']['Value']

        return param_value
    except Exception as e:
        print(f"An error occurred while trying to retrieve parameter {param_name} : {e}")

def get_parameters(path, with_decryption = False):
    """Récupère plusieurs paramètres sous un chemin donné.

    Args:
        path (str): Chemin SSM (ex: ``/app/env``).
        with_decryption (bool): Active le déchiffrement si nécessaire.

    Returns:
        list[dict] | None: Liste d'objets paramètres SSM, sinon ``None`` en cas d'erreur.
    """
    try:
        ssm = boto3.client('ssm', region_name=aws_region_name)

        parameters = ssm.get_parameters_by_path(
            Path=path,
            Recursive=True,
            WithDecryption=with_decryption
        )

        return parameters['Parameters']
    except Exception as e:
        print(f"An error occurred while trying to retrieve parameters by path {path} : {e}")

def extract_parameter(parameter_list, parameter_name):
    """Extrait la valeur d'un paramètre depuis une liste de paramètres SSM.

    Args:
        parameter_list (list[dict]): Liste de paramètres telle que renvoyée par ``get_parameters``.
        parameter_name (str): Fragment/nom à rechercher dans ``Parameter['Name']``.

    Returns:
        str | None: Valeur du paramètre si trouvé, sinon ``None``.
    """
    return next((parameter['Value'] for parameter in parameter_list if parameter_name in parameter['Name']), None)