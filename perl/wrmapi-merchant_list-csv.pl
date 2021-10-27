#!/usr/bin/perl
use REST::Client;
use JSON;
use POSIX;
use Text::CSV;

################################
##
## creds.json file format
##
## {
##  "username": "preferreduser",
##  "password": "secretpw"
## }
##
################################

$creds       = "creds.json";
$csvOutFile  = "merchants.csv";
$apiHost     = "https://api.securetrust.com";

@columns = [
              'Sponsor ID',
              'Unique Merchant ID',
              'MID',
              'Name',
              'DBA',
              'Address 1',
              'Address 2',
              'City',
              'State',
              'Postal Code',
              'Country',
              'Phone',
              'Email',
              'MCC',
              'MCC Segment',
              'MCC Description',
              'Status',
              'Added Via Discovery',
              'In Discovery'
           ];

# Load credentials JSON file
local(*CHF, $/);
open (CFH, '<', $creds) or die "Can't open credentials file $!";
$credsJson = <CFH>;
close CFH;

# Authenticate and save token
print "Authenticating . . . ";
select()->flush();

$tokenClient = REST::Client->new();
$tokenClient->setHost($apiHost);
$tokenClient->POST('/api/token',$credsJson);
if( $tokenClient->responseCode() eq '200' ){
    print "Authenticated\n";
    $tokenData = decode_json($tokenClient->responseContent());
    $idToken = $tokenData->{'idToken'};
    #print "idToken: " . $idToken . "\n";
} else {
    print "Failed to authenticate. HTTP Response: " . $tokenClient->responseCode() . " - " . $tokenClient->responseContent() . "\n";
    exit;
}

# Get count of merchants
print "Getting merchant count . . . ";
select()->flush();
$wrmClient = REST::Client->new();
$wrmClient->setHost($apiHost);
$wrmQueryString = "/wrm/v1/merchants?size=1";
$wrmClient->GET($wrmQueryString, {Authorization => 'Bearer ' . $idToken});
if( $wrmClient->responseCode() eq '200' ){
    print "Done.\n";
    $merchantData = decode_json($wrmClient->responseContent());
    $merchantCount = $merchantData->{'totalItems'};
    print "Merchants: " . $merchantCount . "\n";
} else {
    print "Initial WRM Merchant List query failed. HTTP Response: " . $wrmClient->responseCode() . "\nResponse: " . $wrmClient->responseContent() . "\n";
    exit;
}

# Open output file and write columns header
$csvOut = Text::CSV->new ({ eol => $/, binary => 1 });
$csvOut->eol ("\n");
open $ofh, ">:encoding(utf8)", $csvOutFile or die "$csvOutFile: $!";
$csvOut->print ($ofh, @columns);

# Loop through merchant list requests until we have everything
$listQueries = POSIX::ceil($merchantCount / 100);
for ($queryNum = 1; $queryNum <= $listQueries; $queryNum++) {
    print "Sending merchant list request " . $queryNum . " of " . $listQueries . " . . . ";
    select()->flush();
    $wrmClient = REST::Client->new();
    $wrmClient->setHost($apiHost);
    $wrmQueryString = "/wrm/v1/merchants?size=100&sort-by=name&sort-dir=asc&page=" . $queryNum;
    $wrmClient->GET($wrmQueryString, {Authorization => 'Bearer ' . $idToken});
    if( $wrmClient->responseCode() eq '200' ){
        print "Done.\n";
	$merchantListPage = JSON->new->pretty;
        $merchantListPage = decode_json($wrmClient->responseContent());
	# Loop through merchants
        foreach $merchantRecord(@{$merchantListPage->{'pageItems'}}) {
	    @outputData = ();
	    push @outputData, $merchantRecord->{'sponsorId'};
	    push @outputData, $merchantRecord->{'merchantId'};
	    push @outputData, $merchantRecord->{'mid'};
	    push @outputData, $merchantRecord->{'name'};
	    push @outputData, $merchantRecord->{'dba'};
	    push @outputData, $merchantRecord->{'address1'};
	    push @outputData, $merchantRecord->{'address2'};
	    push @outputData, $merchantRecord->{'city'};
	    push @outputData, $merchantRecord->{'state'};
	    push @outputData, $merchantRecord->{'postalCode'};
	    push @outputData, $merchantRecord->{'country'};
	    push @outputData, $merchantRecord->{'phone'};
	    push @outputData, $merchantRecord->{'email'};
	    push @outputData, $merchantRecord->{'mcc'};
	    push @outputData, $merchantRecord->{'mccSegment'};
	    push @outputData, $merchantRecord->{'mccDescription'};
	    push @outputData, $merchantRecord->{'status'};
	    push @outputData, $merchantRecord->{'discovery'}->{'addedViaDiscovery'};
	    push @outputData, $merchantRecord->{'discovery'}->{'inDiscovery'};
	    $csvOut->print ($ofh, \@outputData);
	}
    } else {
        print "Merchant List query failed. HTTP Response: " . $wrmClient->responseCode() . "\nResponse: " . $wrmClient->responseContent() . "\n";
        exit;
    }
}

# Close output file
print "Closing output file.\n";
close $ofh or die "$outputfile: $!";

# Fin
