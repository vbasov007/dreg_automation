import distance as ds
import re


class CustomerNameDistance:
    @classmethod
    def clear_cust_name(cls, name='') -> str:

        if not isinstance(name, str):
            return ''

        r = name

        r = r.upper()

        r = re.sub(r"[~!?*@#$./']", ' ', r)

        r = re.sub(r"[,-]", ' ', r)

        r = re.sub(r"\bOOO\b", '', r)

        r = re.sub(r"\bZAO\b", '', r)

        r = re.sub(r"\bLTD\b", '', r)

        r = re.sub(r"\bLLC\b", '', r)

        r = re.sub(r"\bFGUP\b", '', r)

        r = re.sub(r"\bJSC\b", '', r)

        r = re.sub(r"\bOAO\b", '', r)

        r = re.sub(r"\bNTC\b", '', r)

        r = re.sub(r"\bNPO\b", '', r)

        r = re.sub(r"\bZAVOD\b", '', r)

        r = re.sub(r"\bNPP\b", '', r)

        # remove double and more spaces
        r = re.sub(r" {2,}", ' ', r)

        r = r.strip()

        return r

    @classmethod
    def compare_word(cls, word1, word2: str) -> float:

        if len(word1) <= 2 or len(word2) <= 2:
            return 1000.0

        if len(word1) >= 5 and len(word2) >= 5:
            if word1.find(word2) != -1 or word2.find(word1) != -1:
                return 0.01

        if len(word1) == 3 and len(word2) == 3:
            if word1 == word2:
                return 0.001
            else:
                return 1000.0
        else:
            return ds.nlevenshtein(word1, word2, method=1)

    @classmethod
    def compare_cust_name(cls, frase1, frase2: str) -> float:

        distances = [1000.0]

        for word1 in frase1.split():
            for word2 in frase2.split():
                if len(word1) >= 3 and len(word2) >= 3:
                    distances.append(cls.compare_word(word1, word2))

        return min(distances)

    @classmethod
    def find_similar_names(cls, orig_name: str, name_list: list, max_distance: float = 0.4) -> list:

        res = list()

        for nm in name_list:
            dist = cls.compare_cust_name(cls.clear_cust_name(nm), cls.clear_cust_name(orig_name))
            if dist < max_distance:
                res.append([nm, dist])
        return res

    @classmethod
    def find_lookslike_as_list(cls, orig_name: str, name_list: list, max_distance: float) -> list:

        res = list()

        for nm in name_list:
            if nm != orig_name:
                dist = cls.compare_cust_name(cls.clear_cust_name(nm), cls.clear_cust_name(orig_name))           
                if dist < max_distance:
                    res.append(nm)
        return res

    @classmethod
    def is_similar_names(cls, orig_name: str, name_list: list, max_distance: float = 0.4):

        if cls.find_similar_names(orig_name, name_list, max_distance):
            return True
        else:
            return False

    @classmethod
    def min_dist(cls, orig_name: str, name_list: list) -> float:

        res_dist = 1000.0

        for nm in name_list:
            dist = cls.compare_cust_name(cls.clear_cust_name(nm), cls.clear_cust_name(orig_name))
            if dist < res_dist:
                res_dist = dist
        return res_dist

    @classmethod
    def find_similar_names_lst(cls, orig_name_list, search_in_list, max_distance):
        res = list()
        for nm in orig_name_list:
            res = res + cls.find_similar_names(nm, search_in_list, max_distance)

        return res

    @classmethod
    def remove_duplicates(cls, lst: list, key_index=0) -> list:
        res = []
        seen = set()

        if key_index == -1:
            for val in lst:
                if val not in seen:
                    res.append(val)
                    seen.add(val)
        else:
            for val in lst:
                if val[key_index] not in seen:
                    res.append(val)
                    seen.add(val[key_index])
        return res

    @classmethod
    def flat_list(cls, l, index=0):
        res = []
        for item in l:
            res.append(item[index])
        return res

    @classmethod
    def list_without_nan_values(cls, lst: list) -> list:
        res = []
        for x in lst:
            if isinstance(x, str):
                res.append(x)
        return res
