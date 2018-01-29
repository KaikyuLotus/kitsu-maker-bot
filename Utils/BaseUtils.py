from Cache import BotCache
from LowLevel import LowLevel
import operator
from collections import OrderedDict

from Core.Error import Unauthorized
from Core import HTTPLL, Manager


def get_ordered_bots():
    ids = Manager.get_bots_id()
    bot_scores = {}
    bot_usages = {}

    for bid in ids:
        bstats = LowLevel.get_stats_file(bid)
        triggers = LowLevel.jfile("t", bid, 0)
        if not triggers:
            Manager.delete_bot(bid)
            continue

        bot_scores[str(bid)] = 0
        bot_usages[str(bid)] = 0

        for trigger in triggers["equals"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 0.5 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["contents"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 0.2 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["interactions"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 1 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["eteractions"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 1.5 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["admin_actions"]:
            if trigger in bstats:
                bot_scores[str(bid)] -= 2 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["bot_commands"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 0.7 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for section in ["insulti", "complimenti", "bene", "amare", "saluti", "scuse", "ringraziamenti"]:
            if section in bstats:
                bot_scores[str(bid)] += 0.7 * bstats[section]
                bot_usages[str(bid)] += 1 * bstats[section]

        for section in ["autom_mattina", "autom_pomeriggio", "autom_sera", "autom_notte"]:
            if section in bstats:
                bot_scores[str(bid)] += 0.3 * bstats[section]
                bot_usages[str(bid)] += 1 * bstats[section]

        if "gen_answ" in bstats:
            bot_scores[str(bid)] += 0.1 * bstats["gen_answ"]
            bot_usages[str(bid)] += 1 * bstats["gen_answ"]

        if "chiamata" in bstats:
            bot_scores[str(bid)] += 0.7 * bstats["chiamata"]
            bot_usages[str(bid)] += 1 * bstats["chiamata"]

    bot_scores = OrderedDict(sorted(bot_scores.items(), key=operator.itemgetter(1), reverse=True))
    return bot_scores, bot_scores, bot_usages


def get_rankings():
    bot_scores, bot_scores, bot_usages = get_ordered_bots()
    rankings = []
    n = 1
    for bid in bot_scores:
        token = Manager.get_token_from_bot_id(bid)
        if token not in BotCache.bots:
            try:
                bot = HTTPLL.getMe(token)
            except Unauthorized:
                continue
            del bot["token"]
            del bot["is_bot"]
            del bot["id"]
            BotCache.bots[token] = bot

        BotCache.bots[token]["score"] = int(bot_scores[str(bid)])
        BotCache.bots[token]["usages"] = bot_usages[str(bid)]
        BotCache.bots[token]["position"] = n

        rankings.append(BotCache.bots[token])
        n += 1

    return rankings


def get_bot_from_rankings(username, ranks):
    for bot in ranks:
        if bot["username"].lower() == username.lower():
            return bot
    return None


def get_com_symbol(entity):
    try:
        return LowLevel.read("triggers.json", entity)["bot_comm_symbol"]
    except Exception:
        return "/"


def get_trigger_list(token, lang_n=0):
    result = {}
    tot = 0
    bid = Manager.get_botid_from_token(token)
    dic = LowLevel.get_triggers(bid, "triggers.json" if lang_n == 0 else "triggers_eng.json")
    sections = ["contents", "equals", "interactions", "eteractions", "bot_commands", "admin_actions"]

    for section in sections:
        tot += len(dic[section])
        result[section] = []
        for trig in dic[section]:
            result[section].append(trig)

    result["total"] = tot
    result["symbol"] = get_com_symbol(bid)

    return result