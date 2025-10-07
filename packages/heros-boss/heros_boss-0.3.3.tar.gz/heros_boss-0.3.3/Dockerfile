# #########################################################################################
# Build image with everything required to run local and remote HEROS via BOSS
# #########################################################################################

FROM registry.gitlab.com/atomiq-project/heros

# Copy the contents of the repository into the image
WORKDIR /git
COPY . boss

# Install BOSS in editable mode
RUN pip install --break-system-packages -e boss/
