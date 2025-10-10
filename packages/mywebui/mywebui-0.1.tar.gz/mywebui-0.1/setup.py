from setuptools import setup, find_packages

setup(
    name="mywebui",                    # પેકેજનું નામ
    version="0.1",                     # પેકેજ વર્ઝન
    packages=find_packages(),         # દરેક ફોલ્ડર auto શોધે
    include_package_data=True,        # assets જેવી files ઉમેરશે
    description="HTML/CSS/JS પેકેજ",
    long_description_content_type="text/markdown",
)
