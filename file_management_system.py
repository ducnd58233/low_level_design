"""
1. Question (these are follow up question, not asked at once)
Design and implement a basic file system manager. The FS manager should provide these functionalities:
- 1. File:
+ create_file: each file has a file_size
+ remove_file: delete file by file name
+ unlink (advanced): manage symbolic links in linux filesystem

- 2. File utility: list - list all files in path with order by file_size DESC, then name by lexicographical order.

- 3. User: 
+ a. add_user: each user has a capacity
+ b. add_file_by_user (chown): if user has enough capacity left for the file_size, then create the file, else return error. 
Need to provide backward compatibility for create_file in part 1
+ c. merge_users: merge the capacity and files ownership of from_user to to_user, after the merge from_user should be deleted.

- 4. Backup and Restore for a user: 
+ a. backup: back up all files by a user
+ b. restore: restore all files by a user, if a file already exists for the user, override it. 
If a file already exists for another user, skip it.

2. Clarify Question
- Is it a local file system or remote file system? (Answer: the API should abstract away the detail of the underlying file system)
- Do we care about how the file content is stored? 
(Answer: again, the API should not care about the underlying storage, e.g. storage format, how the content is stored on disk etc.)
"""

from collections import defaultdict
from dataclasses import dataclass

@dataclass
class File:
    file_name: str
    file_size: int
    
    def __lt__(self, other: 'File'):
        return (self.file_size > other.file_size) or (self.file_size == other.file_size and self.file_name < other.file_name)
    
# external: database, service, etc.
BACKUP = {}

class FileManager:
    def __init__(self):
        self.__files_by_id = defaultdict(int) # <file_name> - file_size in bytes
        self.__user_cap = defaultdict(int)
        self.__files_by_user = defaultdict(set)
        self.__user_cap['admin'] = float('inf')
        
    def __str__(self) -> str:
        return f"files size: {self.__files_by_id}\nfiles by user: {self.__files_by_user}\nuser cap: {self.__user_cap}"
    
    # Part 1: File
    def create_file(self, file_name: str, file_size: int, user: 'str' = 'admin') -> int:
        """
        Returns
            file_size if file_name not exists
            -1 otherwise
        """
        
        if file_name in self.__files_by_id:
            return -1
        
        self.__files_by_id[file_name] = file_size
        return file_size
    
    def remove_file(self, file_name: str) -> int:
        """
        Returns
            file_size if file_name exists
            -1 otherwise
        """
        
        if file_name not in self.__files_by_id:
            return -1
        
        file_size = self.__files_by_id[file_name]
        for user, files in self.__files_by_user.items():
            if file_name in files:
                files.remove(file_name)
        
        del self.__files_by_id[file_name]
        return file_size
    
    # Part 2: File utility
    def list_n_files_by_default_order(self, top_n: int) -> list[File]:
        if top_n > len(self.__files_by_id):
            top_n = len(self.__files_by_id)
        sorted_files = sorted([File(k, v) for k, v in self.__files_by_id.items()])
        return sorted_files[:top_n]
    
    # Part 3: User
    def add_user(self, user_name: str, user_cap: int) -> int:
        if user_name in self.__user_cap:
            return -1
        
        self.__user_cap[user_name] = user_cap
        return user_cap
    
    def add_file_by_user(self, user_name: str, file_name: str, file_size: int) -> int:
        if user_name not in self.__user_cap:
            return -1
        user_cap = self.__user_cap[user_name]
        files_by_user = self._get_file_by_user(user_name)
        total_used = sum(self.__files_by_id[f] for f in files_by_user)
        
        if total_used + file_size > user_cap:
            return -1
        
        result =  self.create_file(file_name, file_size, user_name)
        if result != -1:
            self.__files_by_user[user_name].add(file_name)
        return result
        
    
    def _get_file_by_user(self, user_name: str) -> int:
        return self.__files_by_user.get(user_name, {})
    
    def merge_users(self, to_user: str, from_user) -> int:
        if to_user not in self.__user_cap or from_user not in self.__user_cap:
            print('Ensure both users exists')
            return -1
        
        self.__user_cap[to_user] += self.__user_cap[from_user]
        del self.__user_cap[from_user]
        self.__files_by_user[to_user] = self.__files_by_user[to_user].union(self.__files_by_user[from_user])
        del self.__files_by_user[from_user]
        
        return self.__user_cap[to_user]
    
    # Part 4: Backup and restore
    def backup(self, user_name: str) -> int:
        files_by_user = self._get_file_by_user(user_name) # 1 snapshot
        BACKUP[user_name] = [File(file_name, self.__files_by_id[file_name]) for file_name in files_by_user]
        return sum(f.file_size for f in BACKUP[user_name])
    
    def restore(self, user_name: str) -> int:
        if user_name not in BACKUP:
            return -1
        
        if user_name not in self.__user_cap:
            self.add_user(user_name)
        
        snapshot: list[File] = BACKUP[user_name]
        print(f'backed up snapshot: {snapshot}')
        
        file_owner = dict()
        for user, file_set in self.__files_by_user.items():
            for file_name in file_set:
                file_owner[file_name] = user
        
        current_set = self.__files_by_user[user_name]
        to_delete = current_set.difference(set([file.file_name for file in snapshot]))
        print(f'to delete: {to_delete}')
        
        for file in snapshot:
            if file_owner.get(file.file_name, user_name) != user_name:
                continue
            current_set.add(file.file_name)
            self.__files_by_id[file.file_name] = file.file_size
        
        for file_name in to_delete:
            current_set.remove(file_name)
            del self.__files_by_id[file_name]
            
        return sum(self.__files_by_id[file_name] for file_name in current_set)  
    
if __name__ == '__main__':
    file_manager = FileManager()
    file_manager.create_file('foo', 10)
    file_manager.create_file('foo', 20)
    print(file_manager)
    file_manager.remove_file('foo')
    file_manager.remove_file('foo')
    print(file_manager)
    
    file_manager.create_file('file1', 4096)
    file_manager.create_file('file2', 1024)
    file_manager.create_file('file3', 2048)
    file_manager.create_file('file4', 1024)
    print(file_manager.list_n_files_by_default_order(3))
    
    file_manager.add_user('user1', 2048)
    file_manager.add_user('user2', 2048)
    file_manager.add_file_by_user('user1', 'file5', 2048)
    file_manager.add_file_by_user('user1', 'file6', 2048)
    assert len(file_manager._get_file_by_user('user1')) == 1
    print(file_manager)
    file_manager.merge_users('user1', 'user2')
    file_manager.add_file_by_user('user1', 'file6', 2048)
    assert len(file_manager._get_file_by_user('user1')) == 2
    print(file_manager)

    # Test 4
    print('-' * 100)
    file_manager.add_user('user2', 2048)
    backup_size = file_manager.backup('user1')
    print(f'Backup size: {backup_size}')
    file_manager.remove_file('file5')
    file_manager.remove_file('file6')
    file_manager.add_file_by_user('user1', 'file7', 4096)
    print(file_manager)
    assert len(file_manager._get_file_by_user('user1')) == 1
    file_manager.add_file_by_user('user2', 'file5', 2048)
    restore_size = file_manager.restore('user1')
    print(f'Restored: {restore_size}')
    assert file_manager._get_file_by_user('user1') == set(['file6'])
    print(file_manager)