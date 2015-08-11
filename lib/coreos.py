coreos_ami = { 
    "eu-west-1": { 
        "pv": "ami-0c10417b" 
    },

    "eu-central-1": { 
        "pv": "ami-b8cecaa5" 
    },

    "us-east-1": { 
        'pv': 'ami-3b73d350',
        'hvm': 'ami-3d73d356'
    }
}

image_types = {
    'm1': 'pv',
    'c4': 'hvm'
}

def get_ami(region, instance_type):
    image_type = image_types[instance_type.split('.')[0]]

    return coreos_ami[region][image_type]
