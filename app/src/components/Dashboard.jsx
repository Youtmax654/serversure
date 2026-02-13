import React from 'react'
import { SimpleGrid, Box, Text, Heading, Flex, Badge, Image, Stack, Grid, GridItem } from '@chakra-ui/react'
import { Thermometer, Droplets, Sun, AlertTriangle, Activity, Camera } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useMetrics } from '../hooks/useMetrics'

const MetricCard = ({ title, value, unit, icon: Icon, color, bgGradient, isCritical }) => (
    <Box
        bg="white"
        p={4}
        borderWidth="1px"
        borderColor={isCritical ? 'red.200' : 'gray.100'}
        boxShadow={isCritical ? '0 4px 20px rgba(255, 0, 0, 0.1)' : '0 2px 10px rgba(0,0,0,0.02)'}
        borderRadius="2xl"
        transition="all 0.2s ease-out"
        _hover={{ transform: 'translateY(-4px)', boxShadow: '0 12px 24px rgba(0,0,0,0.1)' }}
        position="relative"
        overflow="hidden"
        gap={4}
    >
        {/* Soft decoration */}
        <Box position="absolute" top="-20%" right="-10%" w="120px" h="120px" bgGradient={bgGradient} opacity={0.1} borderRadius="full" filter="blur(30px)" />

        <Flex justify="space-between" align="start" mb={6}>
            <Box p={3} bg={`${color}10`} borderRadius="xl" color={color}>
                <Icon size={24} />
            </Box>
            {isCritical && <Badge colorScheme="red" variant="subtle" px={3} py={1} borderRadius="full">CRITICAL</Badge>}
        </Flex>
        <Text color="gray.500" fontSize="sm" fontWeight="medium" letterSpacing="wide">{title}</Text>
        <Heading size="3xl" mt={3} color="gray.800" fontWeight="bold">
            {value}
            <Text as="span" fontSize="xl" color="gray.400" ml={2} fontWeight="normal">{unit}</Text>
        </Heading>
    </Box>
)

const Dashboard = ({ ipAddress }) => {
    const { last, history, alerts, photos, loading } = useMetrics(ipAddress)

    if (loading) {
        return (
            <Flex height="50vh" justify="center" align="center" direction="column">
                <Activity size={48} className="animate-pulse" color="#319795" />
                <Text mt={4} color="gray.500" fontWeight="medium">Connecting to sensors...</Text>
            </Flex>
        )
    }

    const isTempCritical = last?.temperature > 30
    const isHumidityCritical = last?.humidity > 70

    const lastAlert = alerts.length > 0 ? alerts[0] : null // Alerts are ordered DESC (newest first)
    const isSystemCritical = (lastAlert?.alert_type === 'ALERT' || lastAlert?.alert_type === 'ALERTE') || isTempCritical || isHumidityCritical

    const systemStatus = isSystemCritical ? 'ALERT' : 'OK'
    const statusColor = isSystemCritical ? "#e53e3e" : "#38a169"
    const statusGradient = isSystemCritical ? "linear(to-br, red.200, pink.200)" : "linear(to-br, green.200, teal.200)"
    const StatusIcon = isSystemCritical ? AlertTriangle : Activity

    // Format history for graph logic 
    const chartData = [...history].reverse().map(h => ({
        time: new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        temp: h.temperature
    }))

    return (
        <Box>
            {/* Metrics Row */}
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8} mb={10} gap={4}>
                <MetricCard
                    title="SYSTEM STATUS"
                    value={systemStatus}
                    unit=""
                    icon={StatusIcon}
                    color={statusColor}
                    bgGradient={statusGradient}
                    isCritical={isSystemCritical}
                />
                <MetricCard
                    title="TEMPERATURE"
                    value={last?.temperature?.toFixed(1) || '--'}
                    unit="°C"
                    icon={Thermometer}
                    color="#e53e3e" // Red-ish for warmth
                    bgGradient="linear(to-br, orange.200, red.200)"
                    isCritical={isTempCritical}
                />
                <MetricCard
                    title="HUMIDITY"
                    value={last?.humidity?.toFixed(0) || '--'}
                    unit="%"
                    icon={Droplets}
                    color={isHumidityCritical ? "#e53e3e" : "#3182ce"}
                    bgGradient={isHumidityCritical ? "linear(to-br, orange.200, red.200)" : "linear(to-br, cyan.200, blue.200)"}
                    isCritical={isHumidityCritical}
                />
                <MetricCard
                    title="LUMINOSITY"
                    value={last?.luminosity?.toFixed(0) || '--'}
                    unit="lx"
                    icon={Sun}
                    color="#d69e2e" // Yellow/Gold
                    bgGradient="linear(to-br, yellow.200, orange.200)"
                />
            </SimpleGrid>

            {/* Main Content Grid */}
            <Grid templateColumns={{ base: "1fr", lg: "3fr 1fr" }} gap={8} mb={10}>

                {/* Chart Section */}
                <GridItem>
                    <Box p={8} bg="white" borderRadius="2xl" borderWidth="1px" borderColor="gray.100" boxShadow="sm" h="450px">
                        <Flex justify="space-between" mb={8} align="center">
                            <Box>
                                <Heading size="md" color="gray.700">Temperature History</Heading>
                                <Text fontSize="sm" color="gray.500" mt={1}>Real-time variations over the last hour</Text>
                            </Box>
                            <Badge variant="subtle" colorScheme="teal" px={3} py={1} borderRadius="full">LIVE</Badge>
                        </Flex>

                        <ResponsiveContainer width="100%" height="80%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#319795" stopOpacity={0.2} />
                                        <stop offset="95%" stopColor="#319795" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    stroke="#a0aec0"
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    minTickGap={40}
                                    dy={10}
                                />
                                <YAxis
                                    stroke="#a0aec0"
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    domain={['dataMin - 2', 'dataMax + 2']}
                                    dx={-10}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#fff', border: 'none', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                                    itemStyle={{ color: '#2c7a7b' }}
                                    labelStyle={{ color: '#718096', marginBottom: '0.25rem' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="temp"
                                    stroke="#319795"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorTemp)"
                                    animationDuration={1500}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </Box>
                </GridItem>

                {/* Alerts Section */}
                <GridItem>
                    <Box p={6} bg="white" borderRadius="2xl" borderWidth="1px" borderColor="gray.100" boxShadow="sm" h="450px" display="flex" flexDirection="column">
                        <Flex justify="space-between" align="center" mb={6}>
                            <Flex align="center" gap={3}>
                                <Box p={2} bg={alerts.length > 0 ? "red.50" : "green.50"} borderRadius="lg">
                                    <AlertTriangle size={20} color={alerts.length > 0 ? "#e53e3e" : "#48bb78"} />
                                </Box>
                                <Heading size="md" color="gray.700">Security Logs</Heading>
                            </Flex>
                            <Badge colorScheme={alerts.length > 0 ? "red" : "green"} variant="subtle" borderRadius="full" px={2}>
                                {alerts.length} New
                            </Badge>
                        </Flex>

                        <Stack spacing={0} overflowY="auto" flex="1" css={{ '&::-webkit-scrollbar': { width: '4px' }, '&::-webkit-scrollbar-track': { background: 'transparent' }, '&::-webkit-scrollbar-thumb': { background: '#edf2f7', borderRadius: '4px' } }}>
                            {alerts.length === 0 ? (
                                <Flex flex="1" justify="center" align="center" direction="column" color="gray.400" bg="gray.50" borderRadius="xl" m={4}>
                                    <Activity size={32} />
                                    <Text mt={3} fontSize="sm" fontWeight="medium">System Secure</Text>
                                </Flex>
                            ) : (
                                <Stack spacing={4}>
                                    {alerts.map((alert, idx) => {
                                        const isAlert = alert.alert_type === 'ALERT' || alert.alert_type === 'ALERTE'
                                        return (
                                            <Flex key={idx} p={3} bg={isAlert ? "red.50" : "green.50"} borderRadius="xl" justify="space-between" align="center" borderLeft="4px solid" borderColor={isAlert ? "red.400" : "green.400"}>
                                                <Flex align="center" gap={3}>
                                                    <Box color={isAlert ? "red.500" : "green.500"}>
                                                        <AlertTriangle size={18} />
                                                    </Box>
                                                    <Box>
                                                        <Text fontSize="sm" fontWeight="bold" color="gray.700">
                                                            {alert.alert_type.replace(/_/g, " ")}
                                                        </Text>
                                                        <Text fontSize="xs" color="gray.500">
                                                            {new Date(alert.timestamp).toLocaleTimeString()} · Value: {alert.value} {alert.value ? 'cm' : ''}
                                                        </Text>
                                                    </Box>
                                                </Flex>
                                            </Flex>
                                        )
                                    })}
                                </Stack>
                            )}
                        </Stack>
                    </Box>
                </GridItem>
            </Grid>

            {/* Photo Gallery Logic - Always shown with placeholders if empty */}
            <Box mb={10} bg="white" borderRadius="2xl" borderWidth="1px" borderColor="gray.100" boxShadow="sm" p={6}>
                <Flex align="center" gap={3} mb={6}>
                    <Box p={2} bg="purple.50" borderRadius="lg" color="purple.500">
                        <Camera size={24} />
                    </Box>
                    <Heading size="lg" color="gray.700">Latest Captures</Heading>
                </Flex>
                <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={6} gap={4}>
                    {photos.length > 0 ? (
                        photos.slice(0, 4).map((photo, i) => (
                            <Box
                                key={i}
                                bg="white"
                                borderRadius="2xl"
                                overflow="hidden"
                                boxShadow="sm"
                                position="relative"
                                role="group"
                                cursor="pointer"
                                transition="all 0.3s"
                                _hover={{ transform: 'translateY(-4px)', boxShadow: 'lg' }}
                            >
                                <Image
                                    src={photo.url}
                                    alt="Intrusion"
                                    objectFit="cover"
                                    w="100%"
                                    h="220px"
                                    filter="grayscale(20%)"
                                    transition="all 0.5s"
                                    _groupHover={{ filter: "grayscale(0%)", transform: "scale(1.05)" }}
                                />
                                <Box
                                    position="absolute"
                                    bottom="0"
                                    left="0"
                                    right="0"
                                    bgGradient="linear(to-t, blackAlpha.800, transparent)"
                                    p={4}
                                    pt={12}
                                >
                                    <Flex justify="space-between" align="end">
                                        <Text fontSize="xs" color="whiteAlpha.900" fontWeight="medium">
                                            CAM_0{i + 1}
                                        </Text>
                                        <Text fontSize="xs" color="whiteAlpha.700">
                                            {new Date().toLocaleDateString()}
                                        </Text>
                                    </Flex>
                                </Box>
                            </Box>
                        ))
                    ) : (
                        // Placeholders when no photos
                        [1, 2, 3, 4].map((_, i) => (
                            <Box
                                key={i}
                                h="220px"
                                bg="gray.50"
                                borderRadius="2xl"
                                border="2px dashed"
                                borderColor="gray.200"
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                                flexDirection="column"
                                color="gray.400"
                            >
                                <Camera size={32} opacity={0.3} />
                                <Text mt={2} fontSize="sm" fontWeight="medium">No Signal</Text>
                            </Box>
                        ))
                    )}
                </SimpleGrid>
            </Box>
        </Box>
    )
}

export default Dashboard
