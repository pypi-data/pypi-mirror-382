import os, time

def main(glob):
    while 1:
        try:
            cd = input("\033[1;32m$cdebug-" + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + ": \033[00m")
            if cd=="exit":
                 break
            cd = cd.replace("\\br","\n")
            if cd and cd[0:1]=="!":
                os.system(cd[1:])
            else:
                exec(cd, glob)
        except Exception as e:
            print(e)

if __name__=="__main__":
    main(globals())