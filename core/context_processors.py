TRANSLATIONS = {
    'pt-br': {
        'operation': 'Operação', 'dashboard': 'Dashboard', 'commercial': 'Comercial', 'leads': 'Leads',
        'clients': 'Clientes', 'engineering': 'Engenharia', 'finance': 'Financeiro', 'management': 'Gestão',
        'plants': 'Usinas', 'team': 'Equipe', 'reports': 'Relatórios', 'language': 'Idioma', 'logout': 'Sair',
        'active_users': 'Usuários ativos', 'solar_systems': 'Sistemas solares', 'new_system': 'Novo sistema',
        'no_plants': 'Nenhuma usina cadastrada.', 'no_users': 'Nenhum usuário ativo.', 'user_management': 'Gestão de usuários',
        'solar_operation': 'Sistemas solares instalados e em acompanhamento.', 'team_description': 'Usuários e responsáveis pela operação do Solar Gest.',
    },
    'en': {
        'operation': 'Operations', 'dashboard': 'Dashboard', 'commercial': 'Sales', 'leads': 'Leads',
        'clients': 'Clients', 'engineering': 'Engineering', 'finance': 'Finance', 'management': 'Management',
        'plants': 'Plants', 'team': 'Team', 'reports': 'Reports', 'language': 'Language', 'logout': 'Sign out',
        'active_users': 'Active users', 'solar_systems': 'Solar systems', 'new_system': 'New system',
        'no_plants': 'No plants registered.', 'no_users': 'No active users.', 'user_management': 'User management',
        'solar_operation': 'Installed solar systems under monitoring.', 'team_description': 'Users and people responsible for Solar Gest operations.',
    },
    'es': {
        'operation': 'Operación', 'dashboard': 'Panel', 'commercial': 'Comercial', 'leads': 'Leads',
        'clients': 'Clientes', 'engineering': 'Ingeniería', 'finance': 'Finanzas', 'management': 'Gestión',
        'plants': 'Plantas', 'team': 'Equipo', 'reports': 'Informes', 'language': 'Idioma', 'logout': 'Salir',
        'active_users': 'Usuarios activos', 'solar_systems': 'Sistemas solares', 'new_system': 'Nuevo sistema',
        'no_plants': 'Ninguna planta registrada.', 'no_users': 'Ningún usuario activo.', 'user_management': 'Gestión de usuarios',
        'solar_operation': 'Sistemas solares instalados y en seguimiento.', 'team_description': 'Usuarios y responsables de la operación de Solar Gest.',
    },
    'it': {
        'operation': 'Operazioni', 'dashboard': 'Dashboard', 'commercial': 'Commerciale', 'leads': 'Lead',
        'clients': 'Clienti', 'engineering': 'Ingegneria', 'finance': 'Finanza', 'management': 'Gestione',
        'plants': 'Impianti', 'team': 'Squadra', 'reports': 'Rapporti', 'language': 'Lingua', 'logout': 'Esci',
        'active_users': 'Utenti attivi', 'solar_systems': 'Impianti solari', 'new_system': 'Nuovo impianto',
        'no_plants': 'Nessun impianto registrato.', 'no_users': 'Nessun utente attivo.', 'user_management': 'Gestione utenti',
        'solar_operation': 'Impianti solari installati e monitorati.', 'team_description': 'Utenti e responsabili delle operazioni Solar Gest.',
    },
    'sq': {
        'operation': 'Operacioni', 'dashboard': 'Paneli', 'commercial': 'Shitje', 'leads': 'Kontakte',
        'clients': 'Klientë', 'engineering': 'Inxhinieri', 'finance': 'Financa', 'management': 'Menaxhim',
        'plants': 'Centralet', 'team': 'Ekipi', 'reports': 'Raporte', 'language': 'Gjuha', 'logout': 'Dilni',
        'active_users': 'Përdorues aktivë', 'solar_systems': 'Sisteme diellore', 'new_system': 'Sistem i ri',
        'no_plants': 'Nuk ka centrale të regjistruara.', 'no_users': 'Nuk ka përdorues aktivë.', 'user_management': 'Menaxhimi i përdoruesve',
        'solar_operation': 'Sisteme diellore të instaluara dhe në monitorim.', 'team_description': 'Përdoruesit dhe përgjegjësit e operacioneve Solar Gest.',
    },
}


def ui(request):
    language = getattr(request, 'LANGUAGE_CODE', 'pt-br')
    return {'ui': TRANSLATIONS.get(language, TRANSLATIONS['pt-br'])}
