#!/usr/bin/python
import argparse
import glob
import video_compression as vc
from panoptes_client import Panoptes, Workflow, Project, SubjectSet, Subject
import os
import datetime


class zoo_video_upload(object):
    def __init__(self,username, password, project_name, subject_set_number, videos_file_path, video_speed_multiplier):
        Panoptes.connect(username=username, password=password)
        self.profile = "ClarkLab/"
        self.project_name = project_name
        self.project_full_name = self.profile + self.project_name
        self.project = Project.find(slug=self.project_full_name)
        self.subject_set_number = subject_set_number
        self.subject_set = SubjectSet.find(self.subject_set_number) #111073
        self.videos_file_path = videos_file_path
        self.temp_dir = self.make_dir(video_directory=self.videos_file_path, new_dir_name="temp_video/")
        self.compressed_video_dir = self.make_dir(video_directory=self.videos_file_path, new_dir_name="compressed_video/")
        self.video_speed_multiplier = video_speed_multiplier

    def make_project(self, project_name, project_description, primary_language='en', private=True):
        try:
            project = Project()
            project.display_name = project_name
            project.description = project_description
            project.primary_language = primary_language
            project.private = private
        except:
            raise 'Project has already been made'

    def make_subject_set(self, project,subject_set_display_name):
        subject_set = SubjectSet()
        subject_set.links.project = project
        subject_set.display_name = subject_set_display_name
        subject_set.save()


    def make_new_single_subject(self, project,subject_set,video_file_path,metadata):
        subject = Subject()
        subject.links.project = project
        subject.add_location(video_file_path)
        subject.metadata.update(metadata)
        subject.save()
        subject_set.add(subject)

    def make_dir(self, video_directory, new_dir_name):
        path = os.path.normpath(video_directory)
        split_dir = path.split(os.sep)
        split_dir[-1] = new_dir_name
        compressed_video_dir = os.sep + os.path.join(*split_dir)
        if not os.path.exists(compressed_video_dir):
            os.makedirs(compressed_video_dir)
        return compressed_video_dir

    def main(self):
        metadata = {'date': str(datetime.datetime.now())}
        videos = glob.glob(self.videos_file_path + "*.mp4")
        for video in videos:
            compressed_vid_file_name = vc.compress_video(video, 50 * 1000, output_file_folder=self.compressed_video_dir)
            if self.video_speed_multiplier!=1: 
                speed_up_video = vc.video_speed(input_file=compressed_vid_file_name, speed_multiplier=self.video_speed_multiplier, output_file_folder=self.temp_dir)
            else:
                speed_up_video = compressed_vid_file_name
            self.make_new_single_subject(project = self.project,
                                        subject_set = self.subject_set,
                                        video_file_path = speed_up_video,
                                        metadata=metadata)


def run(args):
    directory = args.video_fp
    username = args.username
    password = args.password
    video_fp = args.video_fp
    project = args.project
    subject_set = args.subject_set
    speed_multiplier = args.speed_multiplier
    zoo = zoo_video_upload(username = username, 
                           password = password,
                           project_name = project, 
                           subject_set_number = subject_set, 
                           videos_file_path = video_fp,
                           video_speed_multiplier=speed_multiplier)
    zoo.main()



def main():
    parser=argparse.ArgumentParser(description="Input a directory of videos you would like to compress and upload to zooinerse.")
    parser.add_argument("-video_directory_file_path", help="the file path of videos you would like to upload." ,dest="video_fp", type=str, required=True)
    parser.add_argument("-username", help="username to log into zooinerse.", dest="username", type=str, required=True, default=None)
    parser.add_argument("-password", help="password to log into the zooinerse." ,dest="password", type=str, required=True, default=None)
    parser.add_argument("-project_name", help="Name of the project in zooinerse you want to upload to.", dest="project", type=str, required=True, default=None)
    parser.add_argument("-subject_set_number", help="the number associated with the subject set you want to upload too (See Documentation)", dest="subject_set", type=int, required=True, default=None)
    parser.add_argument("-speed_multiplier", help="This is how fast you want to speed up the video (See Documentation)", dest="speed_multiplier", type=int, required=False, default=1)
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)
    

if __name__=="__main__":
    main()
    