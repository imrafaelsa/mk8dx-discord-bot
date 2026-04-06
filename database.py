import sqlite3
import os

DB_PATH = 'mk8dx_bot.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            mmr INTEGER DEFAULT 1000
        )
    ''')
    
    # Tabela de Copas/Partidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id TEXT,
            status TEXT DEFAULT 'open',
            participants TEXT DEFAULT ''
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(discord_id: str) -> bool:
    """Registra um usuário. Retorna True se for novo, False se já existir."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT discord_id FROM users WHERE discord_id = ?', (discord_id,))
    if cursor.fetchone():
        conn.close()
        return False
        
    cursor.execute('INSERT INTO users (discord_id, wins, losses, mmr) VALUES (?, 0, 0, 1000)', (discord_id,))
    conn.commit()
    conn.close()
    return True

def get_user_profile(discord_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_top_players(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY mmr DESC LIMIT ?', (limit,))
    users = cursor.fetchall()
    conn.close()
    return users

def update_user_stats(discord_id: str, mmr_change: int, is_win: bool):
    conn = get_connection()
    cursor = conn.cursor()
    if is_win:
        cursor.execute('UPDATE users SET wins = wins + 1, mmr = mmr + ? WHERE discord_id = ?', (mmr_change, discord_id))
    else:
        cursor.execute('UPDATE users SET losses = losses + 1, mmr = mmr + ? WHERE discord_id = ?', (mmr_change, discord_id))
    conn.commit()
    conn.close()
