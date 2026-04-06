def calculate_elo(winner_mmr: int, average_loser_mmr: int, k_factor: int = 32):
    """
    Calcula a mudança de Elo.
    :param winner_mmr: MMR do vencedor.
    :param average_loser_mmr: MMR médio dos perdedores.
    :param k_factor: Constante de ajuste.
    :return: (pontos ganhos pelo vencedor, pontos perdidos pelos perdedores)
    """
    expected_score_winner = 1 / (1 + 10 ** ((average_loser_mmr - winner_mmr) / 400))
    expected_score_loser = 1 / (1 + 10 ** ((winner_mmr - average_loser_mmr) / 400))

    winner_gain = round(k_factor * (1 - expected_score_winner))
    loser_loss = round(k_factor * (0 - expected_score_loser))

    return winner_gain, loser_loss

def get_rank_name(mmr: int) -> str:
    if mmr < 1000:
        return "🪵 Wood"
    elif 1000 <= mmr < 1500:
        return "🥉 Bronze"
    elif 1500 <= mmr < 2000:
        return "🥈 Silver"
    elif 2000 <= mmr < 2500:
        return "🥇 Gold"
    elif 2500 <= mmr < 3000:
        return "💎 Platinum"
    elif 3000 <= mmr < 3500:
        return "🔮 Diamond"
    else:
        return "👑 Master"
