'''
Implement a group_by_owners function that:

Accepts a dictionary containing the file owner name for each file name.
Returns a dictionary containing a list of file names for each owner name, in any order.
For example, for dictionary {'Input.txt': 'Randy', 'Code.py': 'Stan', 'Output.txt': 'Randy'} the group_by_owners function should return {'Randy': ['Input.txt', 'Output.txt'], 'Stan': ['Code.py']}.
'''
import pandas as pd


class FileOwners:

    @staticmethod
    def group_by_owners(files):
        dt=pd.DataFrame(data={'keys':[*files],'users':[*files.values()]})
        return dt.groupby('users')['keys'].agg(lambda x:list((";".join(x)).split(';'))).to_dict()

files = {
    'Input.txt': 'Randy',
    'Code.py': 'Stan',
    'Output.txt': 'Randy'
}
print(FileOwners.group_by_owners(files))