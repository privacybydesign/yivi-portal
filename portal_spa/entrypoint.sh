if [ -z $VITE_API_ENDPOINT ]; then
    echo "No API endpoint given. Exiting."
    exit 1
fi

find "/app" -type f -exec sed -i 's|'"%VITE_API_ENDPOINT%"'|'"${VITE_API_ENDPOINT}"'|g' {} \;
