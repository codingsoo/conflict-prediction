class git_clone_info:
    git_clone_list = []

    @classmethod
    def get_git_clone_info(self):
        return self.git_clone_info

    @classmethod
    def set_git_clone_info(self, git_info_list):
        self.git_clone_info = git_info_list