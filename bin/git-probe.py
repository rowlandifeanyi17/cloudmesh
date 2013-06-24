from pprint import pprint
from sh import git
from sh import sort
from sh import grep

def git_version():
    return str(git.describe("--tags"))[:-1]

def git_emails(format=None):
    if format==None:
        format_string = "'%aN' <%cE>"
    elif format == 'dict':
        format_string = "%aN\t%cE"
    result = sort (git.log("--all", "--format=" + format_string, _tty_in=True, _tty_out=False, _piped=True), "-u")
    
    if format == None:
        return result
    elif format == "dict":
        list = result.replace("\n", "\t").split("\t")[:-1]
        it = iter(list)
        authors = dict(zip(it, it))
        for name in authors:
            authors[name] = authors[name]
        return authors
    
def git_authors(format=None):
    result = git.shortlog("-s", "-n", _tty_in=True, _tty_out=False)
    if format == None:
        return result
    elif format == "dict":
        list = result.replace("\n", "\t").split("\t")[:-1]
        it = iter(list[::-1])
        authors = dict(zip(it, it))
        for name in authors:
            authors[name] = int(authors[name])
        return authors

def git_info():
    authors = git_authors("dict")
    email = git_emails("dict")

    info = {}
    for name in authors:
        info[name] = {
            "name": name,
            "commits": authors[name],
             "email": email[name]}
    return info

def git_stat(email):
    sum= [0,0,0]
    for line in git.log("--stat", '--author={0}'.format(email), _tty_in=True, _tty_out=False, _iter=True):
        line = line[:-1]
        
        if " files changed" in line:
            line = line.replace(" insertions(+)","")
            line = line.replace(" insertion(+)","")
            line = line.replace(" deletion(-)","")
            line = line.replace(" deletions(-)","")
            line = line.replace(" files changed","")
            line = line.split(",")
            data = [int(i) for i in line]
            for index in range(0,len(data)):
                sum[index] += data[index]

    return {"email": email,
           "fileschanged": sum[0],
           "inserted": sum[1],
           "deleted": sum[2],
           "lineschanges": sum[1] + sum[2],
           }

print git_version()
    
print git_authors()

pprint(git_authors("dict"))

pprint(git_emails())

pprint(git_emails("dict"))

pprint(git_info())

print git_stat("laszewski@gmail.com")

emails = set(git_emails("dict").values())

for email in emails:
    print email
    print git_stat(email)
