import pandas as pd
from customernamedistance import CustomerNameDistance as CusNam
from miscfuncs import remove_duplicates


class CoreCustomerNameSolver:

    @staticmethod
    def process(all_customer_names: list, new_names: list, synonim_database_df):

        synonims_and_anti_synonims_from_file_in_lists = synonim_database_df.values.tolist()

        for name in new_names:
            synonims_and_anti_synonims_from_file_in_lists.append([name])

        already_processed_words = set()

        updated_synonim_list = []

        for row in synonims_and_anti_synonims_from_file_in_lists:

            row = [w for w in row if isinstance(w, str)]

            print("\r", row)

            synonims = [w for w in row if w[0] != '~' and w[0] != '?']

            # skip row if already processed before
            if set(synonims).intersection(already_processed_words):
                continue

            anti_synonims = [w[1:] for w in row if w[0] == '~']
            words_with_questionmark = [w[1:] for w in row if w[0] == '?']

            similar_words_with_distances = CusNam.find_similar_names_lst(synonims, all_customer_names, 0.5)

            new_similar_words = [w[0] for w in similar_words_with_distances]

            new_similar_words = [w for w in new_similar_words if w not in anti_synonims]

            new_similar_words = [w for w in new_similar_words if w not in synonims]

            new_similar_words = [w for w in new_similar_words if w not in words_with_questionmark]

            words_with_questionmark = words_with_questionmark + new_similar_words

            words_with_questionmark.sort()

            synonims = remove_duplicates(synonims)
            anti_synonims = remove_duplicates(anti_synonims)
            words_with_questionmark = remove_duplicates(words_with_questionmark)

            result_row = synonims + ["~" + w for w in anti_synonims] + ["?" + w for w in words_with_questionmark]

            updated_synonim_list.append(result_row)

            already_processed_words.update(set(synonims))

        max_row_word_count = max(len(r) for r in updated_synonim_list)

        headers = ['Core Name'] + ['name' + str(i) for i in range(max_row_word_count - 1)]

        output_df = pd.DataFrame(columns=headers)

        for row in updated_synonim_list:
            output_df = output_df.append(pd.Series(row, index=headers[:len(row)]), ignore_index=True)

        return output_df
    
    @staticmethod
    def process_lookslike(all_customer_names: list, new_names: list, lookslike_database_df: pd.DataFrame, max_dist: float):

        lookslike_db_as_list_of_rows = lookslike_database_df.values.tolist()

        # add new lines of similar lookslike words
        for name in new_names:
            ll_list = CusNam.find_lookslike_as_list(name, all_customer_names, max_dist)
            ll_list = ["?" + w for w in ll_list]
            lookslike_db_as_list_of_rows.append( [name] + ll_list )        

        #convert to sets
        
        work_db = list()
        for row in  lookslike_db_as_list_of_rows:
            row = [w for w in row if isinstance(w, str)]
            r=list()
            r.append({w for w in row if w[0] != '~' and w[0] != '?'}) #r[0] = "ok"
            r.append({w[1:] for w in row if w[0] == '~'}) #r[1] = rejected
            r.append({w[1:] for w in row if w[0] == '?'}) #r[2] = question
            work_db.append(list(r))

            
        for row in work_db:
            for name in row[0]:
                row[2].update( CusNam.find_lookslike_as_list(name, all_customer_names, max_dist) )
            #row[2] = row[2]  - row[0] - row[1]

        
        row_index_for_deletion = list()
        while(True):
            row_index_for_deletion = []    
            num_of_rows = len(work_db)    
            for i in range(num_of_rows-1):
                if i not in row_index_for_deletion:
                    row_i = work_db[i]
                    for j in range(i + 1, num_of_rows):
                        row_j = work_db[j]
                        if j not in row_index_for_deletion:
                            if (row_j[0] & row_i[0]):
                                row_i[0].update(row_j[0])
                                row_i[1].update(row_j[1])
                                row_i[2].update(row_j[2])
                                row_index_for_deletion.append(j)
                    if row_index_for_deletion:
                        work_db[i] = row_i

            if row_index_for_deletion:
                for i in row_index_for_deletion:
                    work_db[i] = None
                work_db = [w for w in work_db if w]

            else:
                break


        #assemble
        lookslike_db_as_list_of_rows = list()

        for row in work_db:       

            row[2] = row[2]  - row[0] - row[1]

            ok = list(row[0])
            ok.sort()
            no = list(row[1])
            no.sort()
            no = ["~" + w for w in no]
           
            q = list(row[2])
            q.sort()
            q = ["?" + w for w in q]

            error = ""
            if (row[0] & row[2]) or (row[0] & row[1]) or (row[1] & row[2]):
                error = "????"

            lookslike_db_as_list_of_rows.append(list(ok + no + q + [error]))

        max_row_word_count = max(len(r) for r in lookslike_db_as_list_of_rows)

        headers = ['Core Name'] + ['name' + str(i) for i in range(max_row_word_count - 1)]

        output_df = pd.DataFrame(columns=headers)

        for row in lookslike_db_as_list_of_rows:
            output_df = output_df.append(pd.Series(row, index=headers[:len(row)]), ignore_index=True)

        return output_df

    @staticmethod
    def get_dict(data_df):

        list_of_rows = data_df.values.tolist()

        dct = {}
        for row in list_of_rows:
            row = [w for w in row if isinstance(w, str)]
            row = [w for w in row if w[:1] != '~' and w[:1] != '?']
            for w in row:
                dct[w] = row[0]

        return dct
