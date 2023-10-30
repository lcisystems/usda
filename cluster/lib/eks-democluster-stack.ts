// lib/my-eks-blueprints-stack.ts
import * as cdk from 'aws-cdk-lib';
import { aws_ec2 as ec2 } from 'aws-cdk-lib'; cdk 
import { aws_eks as eks } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_efs as efs } from 'aws-cdk-lib';

import * as blueprints from '@aws-quickstart/eks-blueprints';
import { TeamPlatform, TeamApplication } from '../teams'; // HERE WE IMPORT TEAMS

export default class ClusterConstruct extends Construct {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id);

    const account = props?.env?.account!;
    const region = props?.env?.region!;
    const stackID = `${id}-blueprint`;



    const EfsCsiDriverAddOn = new blueprints.addons.EfsCsiDriverAddOn();
    const EfsEksOPAAddOn = new blueprints.addons.OpaGatekeeperAddOn();

    const karpenterAddon = new blueprints.addons.KarpenterAddOn({
      requirements: [
          { key: 'node.kubernetes.io/instance-type', op: 'In', vals: ['m5.2xlarge'] },
          { key: 'topology.kubernetes.io/zone', op: 'NotIn', vals: ['us-east-1']},
          { key: 'kubernetes.io/arch', op: 'In', vals: ['amd64','arm64']},
          { key: 'karpenter.sh/capacity-type', op: 'In', vals: ['on-demand']},
      ],
      subnetTags: {
          "Name": `${stackID}/${stackID}-vpc/*`,
      },
      securityGroupTags: {
          [`kubernetes.io/cluster/${stackID}`]: "owned",
      },
      consolidation: { enabled: true },
      ttlSecondsUntilExpired: 2592000,
      weight: 20,
      interruptionHandling: true,
  });
 
    const EksAutoScalerAddOn = new blueprints.ClusterAutoScalerAddOn()

    const clusterProvider = new blueprints.GenericClusterProvider({
      managedNodeGroups: [

        {
          id: "mng1",
          amiType: eks.NodegroupAmiType.AL2_X86_64,
          instanceTypes: [new ec2.InstanceType('m5.2xlarge')],
          desiredSize: 2,
          maxSize: 3, 
          nodeGroupSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
          launchTemplate: {
              // You can pass Custom Tags to Launch Templates which gets propagated to worker nodes.
              tags: {
                  "Name": "Mng1",
                  "Type": "Managed-Node-Group",
                  "LaunchTemplate": "Custom",
                  "Instance": "ONDEMAND"
              }
          }
      },
      ]
    })
 
    const blueprint = blueprints.EksBlueprint.builder()
    .version(cdk.aws_eks.KubernetesVersion.V1_27)
    .clusterProvider(clusterProvider)
    .account(account)
    .region(region)
    .addOns(EfsCsiDriverAddOn, karpenterAddon, EfsEksOPAAddOn)
    .resourceProvider(blueprints.GlobalResources.Vpc, new blueprints.VpcProvider(this.node.tryGetContext('VpdId')))
    .resourceProvider("efs-file-system", new blueprints.CreateEfsFileSystemProvider({name: "efs-file-system",
     }))
    .teams(new TeamPlatform(account), new TeamApplication('dev',account), new TeamApplication('cicd-controlplane',account), new TeamApplication('signed-cicd-controlplane',account)) // HERE WE ONBOARD THE TEAMS
    .build(scope, id+'-stack');


  }
}
